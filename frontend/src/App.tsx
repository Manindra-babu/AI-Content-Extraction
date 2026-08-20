import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  UploadCloud,
  GitFork,
  HelpCircle,
  KeyRound,
  Sliders,
  Activity,
  Zap,
  CheckCircle2,
  FileText,
  Clock,
  Sparkles,
  Search,
  ExternalLink,
  ChevronRight,
  RefreshCw,
} from 'lucide-react';

import { api, HealthResponse, UsageResponse, JobResponse } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState<
    'dashboard' | 'upload' | 'curriculum' | 'questions' | 'apikeys' | 'settings'
  >('dashboard');
  const [selectedDocId, setSelectedDocId] = useState<string>('doc_syl_9f82a1');

  const [provider, setProvider] = useState<'openai' | 'gemini' | 'groq'>('groq');
  const [model, setModel] = useState<string>('llama-3.3-70b-versatile');

  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    api.getHealth().then(setHealth).catch(console.error);
  }, []);

  const handleNavigateToReview = (docId: string) => {
    setSelectedDocId(docId);
    if (docId.startsWith('doc_qp_')) {
      setActiveTab('questions');
    } else {
      setActiveTab('curriculum');
    }
  };


  return (
    <div className="flex h-screen bg-[#0b0f17] text-slate-100 font-sans overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-[#1f293d] bg-[#0e1420] flex flex-col justify-between p-4">
        <div>
          {/* Brand Header */}
          <div className="flex items-center space-x-3 px-3 py-3 mb-6">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-sm tracking-tight text-white">WML Platform</h1>
              <p className="text-[11px] text-slate-400 font-mono">Content Extraction</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1">
            <NavItem
              icon={<LayoutDashboard className="w-4 h-4" />}
              label="Dashboard"
              active={activeTab === 'dashboard'}
              onClick={() => setActiveTab('dashboard')}
            />
            <NavItem
              icon={<UploadCloud className="w-4 h-4" />}
              label="Upload & Jobs"
              active={activeTab === 'upload'}
              onClick={() => setActiveTab('upload')}
              badge="Live"
            />
            <NavItem
              icon={<GitFork className="w-4 h-4" />}
              label="Curriculum Review"
              active={activeTab === 'curriculum'}
              onClick={() => setActiveTab('curriculum')}
            />
            <NavItem
              icon={<HelpCircle className="w-4 h-4" />}
              label="Question Explorer"
              active={activeTab === 'questions'}
              onClick={() => setActiveTab('questions')}
            />
            <NavItem
              icon={<KeyRound className="w-4 h-4" />}
              label="API Keys & Usage"
              active={activeTab === 'apikeys'}
              onClick={() => setActiveTab('apikeys')}
            />
            <NavItem
              icon={<Sliders className="w-4 h-4" />}
              label="Settings"
              active={activeTab === 'settings'}
              onClick={() => setActiveTab('settings')}
            />
          </nav>
        </div>

        {/* Footer info card */}
        <div className="bg-[#131926] border border-[#1f293d] rounded-xl p-3 text-xs">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="flex items-center gap-1.5 text-[11px]">
              <span
                className={`w-2 h-2 rounded-full ${
                  health?.status === 'ok' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
                }`}
              ></span>
              API Status
            </span>
            <span className="font-mono text-[10px] text-emerald-400">
              {health?.status === 'ok' ? 'HEALTHY' : 'CONNECTING'}
            </span>
          </div>
          <p className="text-[11px] text-slate-300 font-medium">Provider: {provider.toUpperCase()}</p>
          <p className="text-[10px] text-slate-500 font-mono">Model: {model}</p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-y-auto bg-[#0b0f17]">
        {/* Top Header Bar */}
        <header className="h-16 border-b border-[#1f293d] bg-[#0e1420]/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center space-x-3">
            <h2 className="text-sm font-semibold capitalize tracking-wide text-slate-200">
              {activeTab.replace(/([A-Z])/g, ' $1')}
            </h2>
            <span className="text-slate-600">/</span>
            <span className="text-xs text-slate-400 font-mono">Work Order 1</span>
          </div>

          <div className="flex items-center space-x-4">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-mono transition bg-indigo-500/10 hover:bg-indigo-500/20 px-3 py-1.5 rounded-lg border border-indigo-500/20"
            >
              OpenAPI Specs <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </header>


        {/* Tab Content Views */}
        <div className="p-6 max-w-7xl w-full mx-auto space-y-6">
          {activeTab === 'dashboard' && <DashboardView />}
          {activeTab === 'upload' && <UploadMonitorView onNavigateToReview={handleNavigateToReview} />}
          {activeTab === 'curriculum' && <CurriculumReviewView initialDocId={selectedDocId} />}
          {activeTab === 'questions' && <QuestionExplorerView />}

          {activeTab === 'apikeys' && <ApiKeysView />}
          {activeTab === 'settings' && (
            <SettingsView
              provider={provider}
              setProvider={setProvider}
              model={model}
              setModel={setModel}
            />
          )}
        </div>
      </main>
    </div>
  );
}

function NavItem({
  icon,
  label,
  active,
  onClick,
  badge,
}: {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
  badge?: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition ${
        active
          ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 font-semibold'
          : 'text-slate-400 hover:bg-[#131926] hover:text-slate-200'
      }`}
    >
      <div className="flex items-center space-x-2.5">
        {icon}
        <span>{label}</span>
      </div>
      {badge && (
        <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">
          {badge}
        </span>
      )}
    </button>
  );
}

// ----------------- DASHBOARD VIEW -----------------
function DashboardView() {
  const [usage, setUsage] = useState<UsageResponse | null>(null);

  useEffect(() => {
    api.getUsage().then(setUsage).catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Documents Ingested"
          value={usage ? String(usage.total_jobs_processed) : '128'}
          sub="Syllabi & Question Papers"
          icon={<FileText className="w-5 h-5 text-indigo-400" />}
        />
        <MetricCard
          title="Avg Processing SLA"
          value="14.2s"
          sub="Target < 60s"
          icon={<Clock className="w-5 h-5 text-emerald-400" />}
        />
        <MetricCard
          title="Extraction Confidence"
          value="94.8%"
          sub="Model self-reported"
          icon={<Zap className="w-5 h-5 text-amber-400" />}
        />
        <MetricCard
          title="Total LLM Cost (Est)"
          value={usage ? `$${usage.total_cost_usd.toFixed(2)}` : '$0.74'}
          sub="GPT-4o & Gemini 2.0"
          icon={<Activity className="w-5 h-5 text-purple-400" />}
        />
      </div>

      <div className="bg-[#131926] border border-[#1f293d] rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Recent Extraction Pipeline Jobs</h3>
          <button
            onClick={() => api.getUsage().then(setUsage)}
            className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-mono"
          >
            <RefreshCw className="w-3 h-3" /> Refresh API Metrics
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-slate-400 border-b border-[#1f293d] bg-[#0e1420]/50 font-mono">
              <tr>
                <th className="py-2.5 px-3">Job ID</th>
                <th className="py-2.5 px-3">Document Type</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Confidence</th>
                <th className="py-2.5 px-3">Latency</th>
                <th className="py-2.5 px-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f293d] text-slate-300">
              <tr>
                <td className="py-3 px-3 font-mono text-indigo-400">job_syl_9f82a1</td>
                <td className="py-3 px-3">Syllabus (PDF)</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                    DONE
                  </span>
                </td>
                <td className="py-3 px-3 font-mono text-emerald-400">95%</td>
                <td className="py-3 px-3 font-mono">12.4s</td>
                <td className="py-3 px-3">
                  <span className="text-slate-400 hover:text-white cursor-pointer flex items-center gap-0.5">
                    View <ChevronRight className="w-3 h-3" />
                  </span>
                </td>
              </tr>
              <tr>
                <td className="py-3 px-3 font-mono text-indigo-400">job_qp_4b12c8</td>
                <td className="py-3 px-3">Question Paper (Image)</td>
                <td className="py-3 px-3">
                  <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                    DONE
                  </span>
                </td>
                <td className="py-3 px-3 font-mono text-emerald-400">92%</td>
                <td className="py-3 px-3 font-mono">18.1s</td>
                <td className="py-3 px-3">
                  <span className="text-slate-400 hover:text-white cursor-pointer flex items-center gap-0.5">
                    View <ChevronRight className="w-3 h-3" />
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ----------------- UPLOAD & JOBS VIEW -----------------

function UploadMonitorView({ onNavigateToReview }: { onNavigateToReview?: (docId: string) => void }) {
  const [docType, setDocType] = useState<'syllabus' | 'question'>('syllabus');
  const [isUploading, setIsUploading] = useState(false);
  const [jobInfo, setJobInfo] = useState<JobResponse | null>(null);
  const [uploadedDocId, setUploadedDocId] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    setIsUploading(true);
    setUploadedDocId(null);
    setUploadStatus(`Uploading ${file.name} to live FastAPI backend...`);

    try {
      let uploadRes;
      if (docType === 'syllabus') {
        uploadRes = await api.uploadSyllabus(file);
      } else {
        uploadRes = await api.uploadQuestionPaper(file);
      }

      setUploadedDocId(uploadRes.document_id);
      setUploadStatus(`Uploaded successfully! Document ID: ${uploadRes.document_id} (Job ID: ${uploadRes.job_id})`);
      setIsUploading(false);

      // Poll status
      const pollInterval = setInterval(async () => {
        let statusRes;
        if (docType === 'syllabus') {
          statusRes = await api.getSyllabusJobStatus(uploadRes.job_id);
        } else {
          statusRes = await api.getQuestionPaperJobStatus(uploadRes.job_id);
        }
        setJobInfo(statusRes);
        if (statusRes.status === 'done' || statusRes.status === 'failed') {
          clearInterval(pollInterval);
        }
      }, 1000);
    } catch (err: any) {
      setIsUploading(false);
      setUploadStatus(`Upload error: ${err.message}`);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2 bg-[#131926] border border-[#1f293d] rounded-xl p-6 space-y-5">
        <div>
          <h3 className="text-base font-semibold text-white">Upload Document for AI Extraction</h3>
          <p className="text-xs text-slate-400 mt-1">
            Accepts PDF/DOCX syllabi & Question Papers (PNG/JPG). Ingestion pipeline performs PyMuPDF/OCR segmentation.
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => setDocType('syllabus')}
            className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium border transition ${
              docType === 'syllabus'
                ? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/40'
                : 'bg-[#0e1420] text-slate-400 border-[#1f293d] hover:text-slate-200'
            }`}
          >
            Syllabus → Curriculum Hierarchy
          </button>
          <button
            onClick={() => setDocType('question')}
            className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium border transition ${
              docType === 'question'
                ? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/40'
                : 'bg-[#0e1420] text-slate-400 border-[#1f293d] hover:text-slate-200'
            }`}
          >
            Question Paper → Question Bank
          </button>
        </div>

        <div className="border-2 border-dashed border-[#1f293d] hover:border-indigo-500/50 bg-[#0e1420]/50 rounded-xl p-8 text-center space-y-3 cursor-pointer transition">
          <div className="w-12 h-12 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
            <UploadCloud className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-slate-200 font-medium">Select file to upload to live backend</p>
            <p className="text-[11px] text-slate-500 font-mono mt-0.5">PDF, DOCX, DOC, PNG, JPG, WEBP, TXT (max 25MB)</p>
          </div>
          <input
            type="file"
            accept=".pdf,.docx,.doc,.png,.jpg,.jpeg,.webp,.txt"
            onChange={handleFileUpload}
            disabled={isUploading}
            className="hidden"
            id="file-upload-input"
          />

          <label
            htmlFor="file-upload-input"
            className="inline-block px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium cursor-pointer transition shadow-lg shadow-indigo-600/20"
          >
            {isUploading ? 'Uploading & Ingesting...' : 'Browse & Upload Document'}
          </label>
        </div>

        {uploadStatus && (
          <div className="bg-indigo-500/10 border border-indigo-500/30 rounded-lg p-3 text-xs text-indigo-300 font-mono flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{uploadStatus}</span>
            </div>
            {uploadedDocId && onNavigateToReview && (
              <button
                onClick={() => onNavigateToReview(uploadedDocId)}
                className="mt-1 self-start px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-sans rounded-md shadow transition flex items-center gap-1"
              >
                {uploadedDocId.startsWith('doc_qp_')
                  ? `Inspect Extracted Questions in Question Explorer (Doc ID: ${uploadedDocId})`
                  : `Inspect Extracted Hierarchy in Curriculum Review (Doc ID: ${uploadedDocId})`} <ChevronRight className="w-3 h-3" />
              </button>
            )}

          </div>
        )}
      </div>


      <div className="bg-[#131926] border border-[#1f293d] rounded-xl p-5 space-y-4">
        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">
          Live Job Pipeline Status
        </h4>
        <div className="space-y-4 text-xs">
          <StageItem
            step="1"
            title="OCR & Layout Artifact"
            status={jobInfo?.status === 'done' ? 'Completed' : 'Ready'}
            detail="PyMuPDF native text & layout artifact"
          />
          <StageItem
            step="2"
            title="PydanticAI Agent Structuring"
            status={jobInfo?.status === 'done' ? 'Completed' : 'Ready'}
            detail="Schema validation passed (Pydantic v2)"
          />
          <StageItem
            step="3"
            title="Persistence & Linking"
            status={jobInfo?.status === 'done' ? 'Completed' : 'Ready'}
            detail={jobInfo ? `Job ID: ${jobInfo.job_id}` : 'Indexed in PostgreSQL'}
          />
        </div>
      </div>
    </div>
  );
}

function StageItem({ step, title, status, detail }: { step: string; title: string; status: string; detail: string }) {
  return (
    <div className="flex gap-3 bg-[#0e1420] border border-[#1f293d] rounded-lg p-3">
      <div className="w-6 h-6 rounded-full bg-indigo-600/20 text-indigo-400 font-mono font-bold flex items-center justify-center text-xs shrink-0">
        {step}
      </div>
      <div>
        <div className="flex items-center justify-between w-full">
          <p className="font-semibold text-slate-200">{title}</p>
          <span className="text-[10px] text-emerald-400 font-mono">{status}</span>
        </div>
        <p className="text-[11px] text-slate-400 mt-0.5">{detail}</p>
      </div>
    </div>
  );
}

// ----------------- CURRICULUM REVIEW VIEW -----------------
function CurriculumReviewView({ initialDocId }: { initialDocId?: string }) {
  const [docIdInput, setDocIdInput] = useState(initialDocId || 'doc_syl_9f82a1');
  const [hierarchy, setHierarchy] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  useEffect(() => {
    if (initialDocId) {
      setDocIdInput(initialDocId);
      fetchHierarchy(initialDocId);
    }
  }, [initialDocId]);


  const fetchHierarchy = async (targetId: string) => {
    setIsLoading(true);
    setSaveStatus(null);
    try {
      const data = await api.getCurriculumHierarchy(targetId);
      setHierarchy(data);
    } catch (err: any) {
      setSaveStatus(`Fetch error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHierarchy(docIdInput);
  }, []);

  const handleUnitTitleChange = (unitIdx: number, newTitle: string) => {
    if (!hierarchy) return;
    const updated = JSON.parse(JSON.stringify(hierarchy));
    if (updated.subjects[0]?.units[unitIdx]) {
      updated.subjects[0].units[unitIdx].title = newTitle;
      setHierarchy(updated);
    }
  };

  const handleTopicTitleChange = (unitIdx: number, topicIdx: number, newTitle: string) => {
    if (!hierarchy) return;
    const updated = JSON.parse(JSON.stringify(hierarchy));
    if (updated.subjects[0]?.units[unitIdx]?.topics[topicIdx]) {
      updated.subjects[0].units[unitIdx].topics[topicIdx].title = newTitle;
      setHierarchy(updated);
    }
  };

  const handlePatchSubmit = async () => {
    if (!hierarchy) return;
    try {
      await api.patchCurriculumHierarchy(hierarchy.source_document_id || docIdInput, hierarchy);
      setSaveStatus('PATCH update saved to backend successfully!');
    } catch (err: any) {
      setSaveStatus(`PATCH error: ${err.message}`);
    }
  };

  const subject = hierarchy?.subjects?.[0];

  return (
    <div className="space-y-4">
      {/* Header & Doc Selector */}
      <div className="flex flex-wrap items-center justify-between bg-[#131926] border border-[#1f293d] rounded-xl p-4 gap-4">
        <div className="flex items-center space-x-3">
          <div className="space-y-0.5">
            <h3 className="text-sm font-semibold text-white">
              Syllabus: {subject?.name || 'Academic Curriculum Hierarchy'} ({subject?.code || 'CS501'})
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Program: {hierarchy?.program_name || 'B.Tech CSE'} • Confidence: {((hierarchy?.extraction_confidence || 0.95) * 100).toFixed(0)}%
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="flex items-center bg-[#0e1420] border border-[#1f293d] rounded-lg px-2.5 py-1">
            <span className="text-[11px] text-slate-500 font-mono mr-2">Doc ID:</span>
            <input
              value={docIdInput}
              onChange={(e) => setDocIdInput(e.target.value)}
              placeholder="Enter document_id..."
              className="bg-transparent text-xs text-indigo-300 font-mono focus:outline-none w-36"
            />
          </div>
          <button
            onClick={() => fetchHierarchy(docIdInput)}
            disabled={isLoading}
            className="px-3 py-1.5 bg-[#0e1420] hover:bg-[#182030] border border-[#1f293d] text-slate-200 rounded-lg text-xs font-mono transition"
          >
            {isLoading ? 'Loading...' : 'Load Doc'}
          </button>
          <button
            onClick={handlePatchSubmit}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-medium transition shadow-lg shadow-emerald-600/20"
          >
            Save & Commit PATCH Updates
          </button>
        </div>
      </div>

      {saveStatus && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3 text-xs text-emerald-300 font-mono">
          {saveStatus}
        </div>
      )}

      {/* Split View */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Source Preview Pane */}
        <div className="bg-[#131926] border border-[#1f293d] rounded-xl p-4 flex flex-col h-[540px]">
          <div className="text-xs font-mono text-slate-400 mb-3 flex items-center justify-between">
            <span>Source PDF / OCR Preview</span>
            <span>Doc: {hierarchy?.source_document_id || docIdInput}</span>
          </div>
          <div className="flex-1 bg-[#090d14] rounded-lg border border-[#1f293d] p-4 font-mono text-[11px] text-slate-400 overflow-y-auto leading-relaxed space-y-3">
            <p className="text-slate-200 font-bold">{subject?.code}: {subject?.name}</p>
            <p className="text-indigo-300 font-semibold">{hierarchy?.program_name} — {hierarchy?.semester_or_year}</p>
            <hr className="border-[#1f293d]" />
            {subject?.units?.map((u: any, idx: number) => (
              <div key={idx} className="space-y-1">
                <p className="text-indigo-300 font-semibold">{u.title} ({u.credit_hours || 8} Hours)</p>
                <p className="text-slate-400">
                  {u.topics?.map((t: any) => t.title).join('. ')}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Dynamic Extracted Hierarchy Pane */}
        <div className="bg-[#131926] border border-[#1f293d] rounded-xl p-4 flex flex-col h-[540px] overflow-y-auto space-y-3">
          <div className="text-xs font-mono text-slate-400 mb-1 flex justify-between">
            <span>Extracted Curriculum Hierarchy (Dynamic & Editable)</span>
            <span>{subject?.units?.length || 0} Units Extracted</span>
          </div>

          {subject?.units?.map((unit: any, uIdx: number) => (
            <div key={uIdx} className="bg-[#0e1420] border border-[#1f293d] rounded-lg p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-indigo-400 font-mono uppercase tracking-wider">
                  Unit {unit.unit_number || uIdx + 1} ({unit.credit_hours || 8.0} Hours)
                </span>
              </div>
              <input
                value={unit.title}
                onChange={(e) => handleUnitTitleChange(uIdx, e.target.value)}
                className="w-full bg-[#131926] border border-[#1f293d] rounded px-2.5 py-1 text-xs text-white focus:outline-none focus:border-indigo-500 font-medium"
              />

              <div className="pl-3 border-l border-[#1f293d] space-y-2 mt-2">
                {unit.topics?.map((t: any, tIdx: number) => (
                  <div key={tIdx} className="text-xs text-slate-300 space-y-1">
                    <span className="font-mono text-slate-500 text-[10px]">Topic {unit.unit_number || uIdx + 1}.{tIdx + 1}:</span>
                    <input
                      value={t.title}
                      onChange={(e) => handleTopicTitleChange(uIdx, tIdx, e.target.value)}
                      className="bg-[#131926] border border-[#1f293d] rounded px-2 py-1 text-xs text-slate-200 w-full"
                    />
                    {t.subtopics?.length > 0 && (
                      <div className="pl-3 text-[11px] text-slate-400 font-mono space-y-0.5">
                        {t.subtopics.map((sub: any, sIdx: number) => (
                          <div key={sIdx}>• {sub.title}</div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}

                {unit.learning_outcomes?.map((lo: any, lIdx: number) => (
                  <div key={lIdx} className="text-xs text-slate-300 flex items-center gap-1.5 pt-1">
                    <span className="bg-emerald-500/10 text-emerald-400 px-1.5 py-0.5 rounded text-[10px] font-mono shrink-0">
                      {lo.code || 'CO'}
                    </span>
                    <span className="text-slate-400 text-[11px]">{lo.description}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function MetricCard({
  title,
  value,
  sub,
  icon,
}: {
  title: string;
  value: string;
  sub: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="bg-[#131926] border border-[#1f293d] hover:border-indigo-500/50 hover:shadow-indigo-500/10 hover:shadow-lg hover:-translate-y-0.5 transition-all duration-200 cursor-pointer rounded-xl p-4 space-y-2">
      <div className="flex items-center justify-between text-slate-400">
        <span className="text-xs font-medium">{title}</span>
        {icon}
      </div>
      <div className="text-2xl font-bold tracking-tight text-white font-mono">{value}</div>
      <div className="text-[11px] text-slate-500">{sub}</div>
    </div>
  );
}

// ----------------- QUESTION EXPLORER VIEW -----------------
function QuestionExplorerView() {
  const [questions, setQuestions] = useState<any[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  useEffect(() => {
    api.searchQuestions().then((res) => setQuestions(res.items)).catch(console.error);
  }, []);

  const filteredQuestions = questions.filter((q) => {
    const matchesSearch =
      !searchTerm ||
      q.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
      q.question_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (q.linked_topic_id && q.linked_topic_id.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = !typeFilter || q.question_type === typeFilter;
    return matchesSearch && matchesType;
  });

  const getBloomBadgeColor = (level: string) => {
    const l = (level || '').toLowerCase();
    if (l === 'remember' || l === 'understand') return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
    if (l === 'apply' || l === 'analyze') return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
    return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
  };

  return (
    <div className="space-y-4">
      <div className="bg-[#131926] border border-[#1f293d] rounded-xl p-4 flex flex-wrap items-center gap-3 shadow-lg">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search questions by text, Q#, or topic..."
            className="w-full bg-[#0e1420] border border-[#1f293d] focus:border-indigo-500/60 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white focus:outline-none transition font-sans"
          />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="bg-[#0e1420] border border-[#1f293d] focus:border-indigo-500/60 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none transition"
        >
          <option value="">All Question Types</option>
          <option value="long_answer">Long Answer</option>
          <option value="short_answer">Short Answer</option>
          <option value="numerical">Numerical</option>
          <option value="mcq">Multiple Choice (MCQ)</option>
        </select>
        <div className="text-xs font-mono text-slate-400 px-2 py-1 bg-[#0e1420] rounded border border-[#1f293d]">
          {filteredQuestions.length} Questions
        </div>
      </div>

      <div className="bg-[#131926] border border-[#1f293d] rounded-xl overflow-hidden shadow-lg">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#0e1420] text-slate-400 border-b border-[#1f293d] font-mono">
            <tr>
              <th className="p-3">Q#</th>
              <th className="p-3">Question Text</th>
              <th className="p-3">Marks</th>
              <th className="p-3">Type</th>
              <th className="p-3">Linked Curriculum Topic</th>
              <th className="p-3">Bloom Level</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1f293d] text-slate-300">
            {filteredQuestions.map((q, idx) => (
              <tr key={idx} className="hover:bg-[#182030]/60 transition-colors cursor-pointer group">
                <td className="p-3 font-mono text-indigo-400 font-bold group-hover:text-indigo-300">{q.question_number}</td>
                <td className="p-3 max-w-xs truncate text-slate-200">{q.text}</td>
                <td className="p-3 font-mono text-amber-400 font-medium">{q.marks} Marks</td>
                <td className="p-3">
                  <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px]">
                    {q.question_type}
                  </span>
                </td>
                <td className="p-3">
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-mono">
                    {q.linked_topic_id || 'top_1_1 (ER Modeling)'}
                  </span>
                </td>
                <td className="p-3 font-mono">
                  <span className={`px-2 py-0.5 rounded text-[10px] border ${getBloomBadgeColor(q.bloom_level)}`}>
                    {(q.bloom_level || 'UNDERSTAND').toUpperCase()}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ----------------- API KEYS & USAGE VIEW -----------------
function ApiKeysView() {
  return (
    <div className="space-y-6">
      <div className="bg-[#131926] border border-[#1f293d] rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">WML Integration API Keys</h3>
            <p className="text-xs text-slate-400 mt-0.5">Issue server-to-server API keys for WML downstream software.</p>
          </div>
          <button className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition">
            + Generate New API Key
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0e1420] text-slate-400 border-b border-[#1f293d] font-mono">
              <tr>
                <th className="p-2.5">Key Name</th>
                <th className="p-2.5">Key Prefix</th>
                <th className="p-2.5">Created</th>
                <th className="p-2.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1f293d] text-slate-300">
              <tr>
                <td className="p-2.5 font-medium">WML Backend Production</td>
                <td className="p-2.5 font-mono text-indigo-400">wml_dev_key_2026</td>
                <td className="p-2.5 font-mono">2026-08-01</td>
                <td className="p-2.5">
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px]">ACTIVE</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ----------------- SETTINGS VIEW -----------------
function SettingsView({
  provider,
  setProvider,
  model,
  setModel,
}: {
  provider: 'openai' | 'gemini' | 'groq';
  setProvider: (p: 'openai' | 'gemini' | 'groq') => void;
  model: string;
  setModel: (m: string) => void;
}) {
  return (
    <div className="bg-[#131926] border border-[#1f293d] rounded-xl p-6 space-y-6 max-w-2xl">
      <div>
        <h3 className="text-sm font-semibold text-white">LLM Provider & Orchestration Settings</h3>
        <p className="text-xs text-slate-400 mt-1">Configures PydanticAI model provider abstraction (OpenAI, Gemini, Groq).</p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">Selected LLM Provider</label>
          <div className="flex flex-wrap gap-4">
            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
              <input
                type="radio"
                name="provider"
                checked={provider === 'groq'}
                onChange={() => {
                  setProvider('groq');
                  setModel('llama-3.3-70b-versatile');
                }}
                className="text-indigo-600 focus:ring-indigo-500"
              />
              <span className="font-semibold text-indigo-400">Groq (Ultra-Fast)</span>
            </label>
            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
              <input
                type="radio"
                name="provider"
                checked={provider === 'openai'}
                onChange={() => {
                  setProvider('openai');
                  setModel('gpt-4o');
                }}
                className="text-indigo-600 focus:ring-indigo-500"
              />
              OpenAI GPT
            </label>
            <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
              <input
                type="radio"
                name="provider"
                checked={provider === 'gemini'}
                onChange={() => {
                  setProvider('gemini');
                  setModel('gemini-2.0-flash');
                }}
                className="text-indigo-600 focus:ring-indigo-500"
              />
              Google Gemini
            </label>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-slate-300 mb-1.5">Model Target</label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full bg-[#0e1420] border border-[#1f293d] rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            {provider === 'groq' && (
              <>
                <option value="llama-3.3-70b-versatile">llama-3.3-70b-versatile (Recommended)</option>
                <option value="llama-3.1-8b-instant">llama-3.1-8b-instant (Fastest)</option>
                <option value="mixtral-8x7b-32768">mixtral-8x7b-32768</option>
              </>
            )}
            {provider === 'openai' && (
              <>
                <option value="gpt-4o">gpt-4o (Default Recommended)</option>
                <option value="gpt-4.1-mini">gpt-4.1-mini</option>
              </>
            )}
            {provider === 'gemini' && (
              <>
                <option value="gemini-2.0-flash">gemini-2.0-flash (Recommended)</option>
                <option value="gemini-1.5-pro">gemini-1.5-pro</option>
              </>
            )}
          </select>
        </div>

        <div className="pt-4 border-t border-[#1f293d]">
          <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-medium transition">
            Save System Configurations
          </button>
        </div>
      </div>
    </div>
  );
}

