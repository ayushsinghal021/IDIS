const BASE_URL = 'http://127.0.0.1:8000';

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('process_now', 'true'); // Must be string 'true'

  try {
    const response = await fetch('http://127.0.0.1:8000/api/documents/upload', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      // Log exact backend error
      const errorText = await response.text();
      console.error("Backend error:", errorText);
      throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  } catch (error) {
    console.error("Upload failed:", error);
    throw new Error(`Request failed: ${error.message}`);
  }
};

// Perform Q&A
export const askQuestion = async (question) => {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error('Failed to get an answer');
  }

  return response.json();
};

// Export data
export const exportData = async (format) => {
  const response = await fetch(`${BASE_URL}/export?format=${format}`);

  if (!response.ok) {
    throw new Error('Failed to export data');
  }

  return response.blob();
};