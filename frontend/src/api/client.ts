const API_BASE_URL = '/v1';
const DEV_API_KEY = 'wml_dev_key_2026';

export interface HealthResponse {
  status: string;
  environment: string;
  services: {
    database: string;
    redis: string;
    llm: {
      provider: string;
      model: string;
      configured: boolean;
    };
    storage: string;
  };
}

export interface UploadResponse {
  job_id: string;
  document_id: string;
  filename: string;
  status: string;
  message: string;
}

export interface JobResponse {
  job_id: string;
  document_id: string;
  status: string;
  created_at: string;
  completed_at?: string;
  error?: string;
  progress_percentage: number;
}

export interface UsageResponse {
  total_jobs_processed: number;
  total_tokens_used: number;
  total_cost_usd: number;
  provider_breakdown: Record<string, any>;
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    'X-API-Key': DEV_API_KEY,
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `HTTP ${response.status} Request Error`);
  }

  return response.json();
}

export const api = {
  getHealth: () => request<HealthResponse>('/health'),

  uploadSyllabus: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<UploadResponse>('/syllabus/upload', {
      method: 'POST',
      body: formData,
    });
  },

  getSyllabusJobStatus: (jobId: string) => request<JobResponse>(`/syllabus/jobs/${jobId}`),

  getCurriculumHierarchy: (documentId: string) => request<any>(`/syllabus/${documentId}`),

  patchCurriculumHierarchy: (documentId: string, payload: any) =>
    request<any>(`/syllabus/${documentId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),

  uploadQuestionPaper: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<UploadResponse>('/questions/upload', {
      method: 'POST',
      body: formData,
    });
  },

  getQuestionPaperJobStatus: (jobId: string) => request<JobResponse>(`/questions/jobs/${jobId}`),

  getQuestionPaper: (documentId: string) => request<any>(`/questions/${documentId}`),

  searchQuestions: (params: Record<string, string | number> = {}) => {
    const queryString = new URLSearchParams(
      Object.entries(params).map(([k, v]) => [k, String(v)])
    ).toString();
    return request<any>(`/question-bank/search?${queryString}`);
  },

  linkTopics: (curriculumDocId: string, questionDocId: string) =>
    request<any>('/question-bank/link-topics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        curriculum_document_id: curriculumDocId,
        question_paper_document_id: questionDocId,
      }),
    }),

  getUsage: () => request<UsageResponse>('/usage'),
};
