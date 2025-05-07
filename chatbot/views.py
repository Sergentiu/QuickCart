import json
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatMessage  # Chat history model

# ---------------- Chat Page View ----------------
def chat_page(request):
    """
    Renders a page with an existing chat history for authenticated users.
    If the user is not authenticated, it shows an empty history.
    """
    if not request.user.is_authenticated:
        return render(request, 'chat.html', {"history": []})

    history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
    return render(request, 'chat.html', {"history": history})

# ---------------- Process Message View ----------------
@csrf_exempt
def process_message(request):
    """
    Handles AJAX POST requests with a JSON payload: {"message": "..."}.
    Sends user input to Rasa and retrieves the response.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        query = data.get('message', '').strip()

        if not request.user.is_authenticated:
            return JsonResponse({"response": "You must be logged in to use the chatbot."}, status=401)

        # Store the user message in the database
        ChatMessage.objects.create(user=request.user, sender='user', message=query)

        # Send the message to Rasa
        rasa_url = "http://localhost:5005/webhooks/rest/webhook"
        payload = {"sender": str(request.user.username), "message": query}
        try:
            rasa_response = requests.post(rasa_url, json=payload)
            bot_response_data = rasa_response.json()

            if bot_response_data:
                bot_reply = bot_response_data[0].get("text", "I'm not sure how to respond.")
            else:
                bot_reply = "I didn't understand that."

        except requests.exceptions.RequestException:
            bot_reply = "Error connecting to chatbot server."

        # Store the bot response in the database
        ChatMessage.objects.create(user=request.user, sender='bot', message=bot_reply)

        return JsonResponse({"response": bot_reply})

    return JsonResponse({'error': 'Invalid HTTP method. Use POST.'}, status=405)