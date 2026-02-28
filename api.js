const API_BASE_URL = 'http://127.0.0.1:8000'; 

/**
 * Sends code to the FastAPI review endpoint.
 * Fetches: original_score, refined_score, original_time_complexity, 
 * original_space_complexity, time_complexity, space_complexity, etc.
 */
export const reviewCode = async (code) => {
  try {
    const response = await fetch(`${API_BASE_URL}/review`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json' 
      },
      body: JSON.stringify({ code }), // Matches 'code' in Python CodeRequest
    });

    // Handle non-200 responses (like 422 or 500)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server Error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("Critical API Failure (Review):", error);
    throw error;
  }
};

/**
 * Translates the refined code into the target language.
 * Explicitly maps 'targetLanguage' to 'target_language' for the Backend.
 */
export const translateCode = async (code, targetLanguage) => {
  if (!code || !targetLanguage) return null;

  try {
    const response = await fetch(`${API_BASE_URL}/translate`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json' 
      },
      body: JSON.stringify({ 
        code: code, 
        target_language: targetLanguage // Matches 'target_language' in Python TranslateRequest
      }),
    });

    if (!response.ok) {
      throw new Error(`Translation failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("Critical API Failure (Translate):", error);
    throw error;
  }
};