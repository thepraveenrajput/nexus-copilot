import re


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
):
    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    chunks = []
    current_sentences = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        sentence_length = len(sentence)

        # Handle a sentence larger than chunk_size
        if sentence_length > chunk_size:
            if current_sentences:
                chunks.append(
                    " ".join(current_sentences)
                )
                current_sentences = []
                current_length = 0

            chunks.append(sentence)
            continue

        additional_length = (
            sentence_length
            if not current_sentences
            else sentence_length + 1
        )

        # Sentence fits in current chunk
        if (
            current_length + additional_length
            <= chunk_size
        ):
            current_sentences.append(sentence)
            current_length += additional_length
            continue

        # Save current chunk
        previous_sentences = current_sentences

        chunks.append(
            " ".join(previous_sentences)
        )

        # Build sentence-level overlap.
        # Only include COMPLETE sentences.
        overlap_sentences = []
        overlap_length = 0

        for previous_sentence in reversed(
            previous_sentences
        ):
            sentence_len = len(previous_sentence)

            # Never cut a sentence to create overlap.
            if (
                overlap_length + sentence_len
                > overlap
            ):
                break

            overlap_sentences.insert(
                0,
                previous_sentence,
            )

            overlap_length += sentence_len

            # Account for spaces between sentences.
            if len(overlap_sentences) > 1:
                overlap_length += 1

        current_sentences = (
            overlap_sentences + [sentence]
        )

        current_length = len(
            " ".join(current_sentences)
        )

    if current_sentences:
        chunks.append(
            " ".join(current_sentences)
        )

    return chunks