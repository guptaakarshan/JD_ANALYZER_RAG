import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 60000, // 60 s — embedding + LLM calls can be slow
});

/**
 * Extracts a human-readable error message from an Axios error or a
 * backend JSON response that includes an `error` field.
 */
export function getErrorMessage(err) {
  // Backend returned a 2xx JSON body with { error: "..." }
  if (err?.response?.data?.error) return err.response.data.error;
  // HTTP error with a detail message (FastAPI validation errors)
  if (err?.response?.data?.detail) {
    const detail = err.response.data.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map((d) => d.msg).join(', ');
  }
  // Network / timeout
  if (err?.code === 'ECONNABORTED') return 'Request timed out. The backend may be busy — please try again.';
  if (err?.message === 'Network Error') return 'Cannot reach the backend. Make sure the server is running on ' + BASE_URL;
  return err?.message || 'An unexpected error occurred.';
}

// ─── Endpoints ────────────────────────────────────────────────────────────────

/**
 * POST /upload-pdf
 * Sends the PDF as multipart/form-data.
 * Returns: { session_id, filename, total_pages, total_chunks, vector_store_created, faiss_index_location }
 */
export async function uploadPdf(file, sessionId) {
  const form = new FormData();
  form.append('file', file);
  if (sessionId) form.append('session_id', sessionId);

  const { data } = await api.post('/upload-pdf', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    params: sessionId ? { session_id: sessionId } : {},
  });

  // Backend returns { error } even on 200 when something goes wrong
  if (data?.error) throw new Error(data.error);
  return data;
}

/**
 * POST /upload-jd
 * Body: { job_description: string, session_id?: string }
 * Returns: { session_id, message, total_chunks }
 */
export async function uploadJd(jobDescription, sessionId) {
  const { data } = await api.post('/upload-jd', {
    job_description: jobDescription,
    session_id: sessionId,
  });

  if (data?.error) throw new Error(data.error);
  return data;
}

/**
 * POST /ask
 * Body: { query: string, session_id: string }
 * Returns: { question, answer }
 */
export async function askQuestion(query, sessionId) {
  const { data } = await api.post('/ask', {
    query,
    session_id: sessionId,
  });

  if (data?.error) throw new Error(data.error);
  return data; // { question, answer }
}
