# core/ai_integrator.py
# This component handles all communication with external AI models.

import threading
import queue
import logging
from typing import Dict, Any

# --- DevOS Component: AIIntegration ---
class AIIntegrator:
    """
    Handles communication with an external AI model asynchronously.
    It uses a queue to manage requests and a worker thread to process them,
    ensuring the main application remains responsive.
    """
    def __init__(self):
        self.request_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logging.info("AI Integrator initialized and worker thread started.")

    def _worker_loop(self):
        """Worker thread loop to process AI requests."""
        while True:
            try:
                task_id, request_data = self.request_queue.get()
                logging.info(f"Processing AI request for task_id: {task_id}")

                # --- Placeholder for actual API call ---
                # This is where you would integrate with a real LLM API.
                # The code below simulates a response.

                try:
                    prompt = request_data.get("prompt", "")

                    # Example of a real API call using 'requests' library:
                    # import requests
                    # api_key = os.environ.get("GEMINI_API_KEY") # Recommended practice
                    # if not api_key:
                    #     raise ValueError("Gemini API key not found.")
                    #
                    # headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
                    # payload = {"prompt": prompt, "max_tokens": 500}
                    # response = requests.post("https://api.gemini.ai/v1/generate", headers=headers, json=payload, timeout=60)
                    # response.raise_for_status() # Raise an exception for bad status codes
                    # result = response.json()
                    # ai_text_response = result.get("choices")[0].get("text")

                    # Simulated response for demonstration
                    logging.info("Simulating AI response...")
                    ai_text_response = (
                        f"// AI-generated code based on prompt:\n"
                        f"// '{prompt}'\n"
                        f"\ndef bubble_sort(arr):\n"
                        f"    n = len(arr)\n"
                        f"    for i in range(n):\n"
                        f"        for j in range(0, n-i-1):\n"
                        f"            if arr[j] > arr[j+1]:\n"
                        f"                arr[j], arr[j+1] = arr[j+1], arr[j]\n"
                        f"    return arr\n"
                    )

                    self.result_queue.put((task_id, {"success": True, "response": ai_text_response}))

                except Exception as e:
                    logging.error(f"Error in AI processing: {e}")
                    self.result_queue.put((task_id, {"success": False, "error": str(e)}))

                self.request_queue.task_done()

            except Exception as e:
                logging.error(f"Critical error in AI worker loop: {e}")

    def add_request(self, task_id: str, prompt: str):
        """Adds a new AI request to the queue."""
        request_data = {"prompt": prompt}
        self.request_queue.put((task_id, request_data))
        logging.info(f"AI request added to queue for task_id: {task_id}")

    def get_result(self, timeout: int = 1) -> Any:
        """Tries to get a result from the queue, non-blocking."""
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None

