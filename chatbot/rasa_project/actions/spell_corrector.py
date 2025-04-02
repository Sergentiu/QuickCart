from __future__ import annotations
from typing import Any, Dict, List, Text
import os

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.storage.resource import Resource
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.constants import TEXT
from rasa.engine.recipes.default_recipe import DefaultV1Recipe

from symspellpy.symspellpy import SymSpell, Verbosity

@DefaultV1Recipe.register([GraphComponent], is_trainable=False)
class SpellCorrector(GraphComponent):
    """A custom component for spelling correction using SymSpellPy."""

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        return {
            "max_edit_distance": 2,
            "prefix_length": 7,
            "corpus_path": "data/spell_corpus.txt",
        }

    def __init__(self, config: Dict[Text, Any]) -> None:
        self.config = config
        self.sym_spell = SymSpell(
            max_dictionary_edit_distance=self.config["max_edit_distance"],
            prefix_length=self.config["prefix_length"],
        )
        corpus_path = self.config["corpus_path"]
        if not os.path.isabs(corpus_path):
            corpus_path = os.path.join(os.getcwd(), corpus_path)
        self.sym_spell.load_dictionary(corpus_path, term_index=0, count_index=1)

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> SpellCorrector:
        return cls(config)

    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            original_text = message.get(TEXT, "")
            suggestion = self.sym_spell.word_segmentation(original_text)
            corrected_text = suggestion.corrected_string
            message.set(TEXT, corrected_text)
        return messages