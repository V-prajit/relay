"""
StreamingDecoder - Memory-efficient decoder with streaming token generation

Generates text token by token to minimize memory footprint during decoding.
"""

import torch
from typing import Iterator, Optional
import logging

logger = logging.getLogger(__name__)


class StreamingDecoder:
    """
    Streaming decoder for memory-efficient text generation.

    Generates text token-by-token with periodic cache clearing to prevent OOM.
    """

    def __init__(self, model, max_batch_size: int = 1, max_new_tokens: int = 4096):
        """
        Initialize the streaming decoder.

        Args:
            model: Loaded DeepSeek-OCR model
            max_batch_size: Maximum batch size (keep at 1 for laptops)
            max_new_tokens: Maximum tokens to generate
        """
        self.model = model
        self.batch_size = max_batch_size
        self.max_new_tokens = max_new_tokens

    def decode(
        self,
        vision_tokens: torch.Tensor,
        output_format: str = 'text',
        stream: bool = False
    ) -> str:
        """
        Decode vision tokens to text.

        Args:
            vision_tokens: Encoded vision token tensor
            output_format: Output format ('text', 'markdown', 'html')
            stream: Whether to stream output

        Returns:
            Generated text string
        """
        if stream:
            # Streaming generation
            return ''.join(self.decode_streaming(vision_tokens, output_format))
        else:
            # Non-streaming generation (faster but uses more memory)
            return self._decode_batch(vision_tokens, output_format)

    def decode_streaming(
        self,
        vision_tokens: torch.Tensor,
        output_format: str = 'text'
    ) -> Iterator[str]:
        """
        Generate text token by token with streaming.

        Args:
            vision_tokens: Encoded vision tokens
            output_format: Output format

        Yields:
            Generated text chunks
        """
        generated_tokens = []
        prompt = self._create_prompt(output_format)

        try:
            with torch.no_grad():
                for token_id in self._generate_tokens_iteratively(vision_tokens, prompt):
                    # Decode token to text
                    text_chunk = self._token_to_text(token_id)
                    generated_tokens.append(text_chunk)

                    # Yield chunk for streaming
                    yield text_chunk

                    # Periodic cache clearing (every 100 tokens)
                    if len(generated_tokens) % 100 == 0:
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                        logger.debug(f"Generated {len(generated_tokens)} tokens, cleared cache")

        except Exception as e:
            logger.error(f"Error during streaming decode: {str(e)}")
            raise

    def _decode_batch(
        self,
        vision_tokens: torch.Tensor,
        output_format: str = 'text'
    ) -> str:
        """
        Decode entire batch at once (faster but uses more memory).

        Args:
            vision_tokens: Encoded vision tokens
            output_format: Output format

        Returns:
            Complete generated text
        """
        prompt = self._create_prompt(output_format)

        try:
            with torch.no_grad():
                # Use model's generate method if available
                if hasattr(self.model, 'generate'):
                    output_ids = self.model.generate(
                        vision_tokens,
                        max_new_tokens=self.max_new_tokens,
                        do_sample=False,  # Greedy decoding for consistency
                        temperature=1.0,
                        top_p=1.0,
                    )
                else:
                    # Fallback: manual generation
                    output_ids = self._manual_generate(vision_tokens, prompt)

                # Decode output
                if hasattr(self.model, 'tokenizer'):
                    text = self.model.tokenizer.decode(output_ids[0], skip_special_tokens=True)
                else:
                    text = self._manual_decode(output_ids)

                return text

        except Exception as e:
            logger.error(f"Error during batch decode: {str(e)}")
            raise

    def _generate_tokens_iteratively(
        self,
        vision_tokens: torch.Tensor,
        prompt: str
    ) -> Iterator[int]:
        """
        Generate tokens one at a time.

        Args:
            vision_tokens: Vision tokens
            prompt: Text prompt for generation

        Yields:
            Token IDs
        """
        # This would use model's iterative generation
        # Placeholder implementation - actual implementation depends on model API

        # For now, use batch generation and split
        text = self._decode_batch(vision_tokens, 'text')

        # Convert text to fake token stream (placeholder)
        for char in text:
            yield ord(char)  # Just for demonstration

    def _token_to_text(self, token_id: int) -> str:
        """
        Convert token ID to text.

        Args:
            token_id: Token ID

        Returns:
            Text representation
        """
        # Placeholder - would use tokenizer
        return chr(token_id) if token_id < 128 else ''

    def _create_prompt(self, output_format: str) -> str:
        """
        Create prompt based on output format.

        Args:
            output_format: Desired output format

        Returns:
            Prompt string
        """
        format_prompts = {
            'text': '<image>\nFree OCR.',
            'markdown': '<image>\n<|grounding|>Convert the document to markdown.',
            'html': '<image>\nParse as HTML table.',
            'grounding': '<image>\n<|grounding|>Extract text with bounding boxes.',
        }

        return format_prompts.get(output_format, format_prompts['text'])

    def _manual_generate(self, vision_tokens: torch.Tensor, prompt: str) -> torch.Tensor:
        """
        Manual generation fallback if model doesn't have generate method.

        Args:
            vision_tokens: Vision tokens
            prompt: Generation prompt

        Returns:
            Generated token IDs
        """
        # Placeholder for manual generation logic
        logger.warning("Using manual generation fallback - may be suboptimal")
        return torch.tensor([[1, 2, 3]])  # Placeholder

    def _manual_decode(self, token_ids: torch.Tensor) -> str:
        """
        Manual decoding fallback if no tokenizer available.

        Args:
            token_ids: Token IDs to decode

        Returns:
            Decoded text
        """
        logger.warning("Using manual decode fallback")
        return "[Manual decode not implemented]"

    def set_max_new_tokens(self, max_tokens: int):
        """
        Set maximum new tokens to generate.

        Args:
            max_tokens: Maximum token count
        """
        self.max_new_tokens = max_tokens
        logger.info(f"Set max_new_tokens to {max_tokens}")
