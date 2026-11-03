expansion_prompt = """
Tu reformules des questions pour un moteur de recherche RAG.

Génère exactement 3 variantes courtes de la question.
Ne réponds JAMAIS à la question.
Aucune explication, aucun titre, aucun Markdown.
Une seule question par ligne, maximum 10 mots.

Question : {question}
"""
