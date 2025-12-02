import { useState } from "react";
import toast, { Toaster } from "react-hot-toast";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function Skeleton({ className }: { className?: string }) {
  return <div className={`animate-pulse bg-slate-800/60 rounded ${className}`} />;
}

export default function App() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [fileHistory, setFileHistory] = useState<string[]>([]);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [answerLoading, setAnswerLoading] = useState(false);

  const [extraction, setExtraction] = useState<any>(null);
  const [extractionLoading, setExtractionLoading] = useState(false);

  // ----------------------------------------
  // 1. Upload PDFs
  // ----------------------------------------
  const uploadFiles = async () => {
    if (!files || files.length === 0) {
      setUploadStatus("❌ No files selected.");
      toast.error("No files selected.");
      return;
    }

    setUploading(true);
    setUploadStatus(
      "⏳ Upload started… Extracting text & chunking (may take 1–3 minutes)…"
    );

    toast.dismiss();
    const loadingToast = toast.loading(
      "Uploading & processing PDF(s)… large drawings may take 1–3 minutes"
    );

    const form = new FormData();
    for (let i = 0; i < files.length; i++) {
      form.append("files", files[i]);
    }

    try {
      const res = await fetch(`${API_URL}/ingest/`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        setUploadStatus("❌ Upload failed. Backend error.");
        toast.dismiss(loadingToast);
        toast.error("Upload failed. Check backend logs.");
        return;
      }

      const data = await res.json();
      const totalChunks = data.ingested?.[0]?.chunks ?? "?";
      const uploadedNames = Array.from(files).map((f) => f.name);

      setUploadStatus(`✅ Upload complete (${totalChunks} chunks).`);
      setFileHistory((prev) => [...prev, ...uploadedNames]);

      toast.dismiss(loadingToast);
      toast.success(`Uploaded ${uploadedNames.length} file(s) successfully.`);
    } catch (err) {
      console.error(err);
      setUploadStatus("❌ Network error.");
      toast.dismiss(loadingToast);
      toast.error("Network error. Backend unreachable.");
    } finally {
      setUploading(false);
    }
  };

  // ----------------------------------------
  // 2. Chat / Ask a Question
  // ----------------------------------------
  const askQuestion = async () => {
    if (!question.trim()) return;

    setAnswerLoading(true);
    setAnswer(null);

    try {
      const res = await fetch(`${API_URL}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question }),
      });

      const data = await res.json();
      setAnswer(data.answer || "No answer returned.");
    } catch (err) {
      console.error(err);
      setAnswer("❌ Chat request failed.");
    } finally {
      setAnswerLoading(false);
    }
  };

  // ----------------------------------------
  // 3. Door Schedule Extraction
  // ----------------------------------------
  const extractDoorSchedule = async () => {
    setExtractionLoading(true);
    setExtraction(null);

    try {
      const res = await fetch(`${API_URL}/extract/door-schedule`, {
        method: "POST",
      });

      const data = await res.json();
      setExtraction(data);
    } catch (err) {
      console.error(err);
      setExtraction({ error: "Extraction failed." });
    } finally {
      setExtractionLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Toaster position="bottom-right" />

      {/* HEADER */}
      <header className="border-b border-slate-800 px-10 py-6">
        <h1 className="text-2xl font-bold">Constructure AI — RAG Sandbox</h1>
        <p className="text-xs text-slate-500 mt-1">
          Backend:{" "}
          <span className="font-mono">
            {API_URL || "VITE_API_URL not configured"}
          </span>
        </p>
      </header>

      <main className="px-10 py-8 space-y-8 max-w-5xl mx-auto">

        {/* ------------------------ */}
        {/* 1. PDF INGEST */}
        {/* ------------------------ */}
        <section className="border border-slate-800 rounded-xl p-6 bg-slate-900/40">
          <h2 className="text-xl font-semibold mb-3">1. Ingest PDFs</h2>
          <p className="text-sm mb-4 text-slate-400">
            Upload document PDFs. Large drawings (e.g., Attachment 7) may take 1–3 minutes.
          </p>

          {/* Hidden input */}
          <input
            type="file"
            id="fileInput"
            multiple
            className="hidden"
            onChange={(e) => setFiles(e.target.files)}
          />

          <div className="flex items-center gap-3">

            {/* Choose Files Button */}
            <button
              onClick={() => document.getElementById("fileInput")!.click()}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-medium"
            >
              Choose Files
            </button>

            {/* Upload Button */}
            <button
              onClick={uploadFiles}
              disabled={uploading}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                uploading
                  ? "bg-blue-800 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {uploading ? "Uploading…" : "Upload"}
            </button>
          </div>

          {/* Selected file names */}
          {files && files.length > 0 && (
            <p className="mt-2 text-sm text-slate-400">
              Selected: {Array.from(files).map((f) => f.name).join(", ")}
            </p>
          )}

          {/* Upload Status */}
          {uploadStatus && (
            <p className="text-sm text-slate-300 mt-2">{uploadStatus}</p>
          )}

          {/* Upload History */}
          {fileHistory.length > 0 && (
            <div className="mt-4 p-3 bg-slate-900 border border-slate-800 rounded-lg">
              <h3 className="text-sm font-semibold mb-2">
                Uploaded files this session
              </h3>
              <ul className="text-xs text-slate-300 space-y-1">
                {fileHistory.map((name, idx) => (
                  <li key={idx}>• {name}</li>
                ))}
              </ul>
            </div>
          )}
        </section>

        {/* ------------------------ */}
        {/* 2. Chat / Q&A */}
        {/* ------------------------ */}
        <section className="border border-slate-800 rounded-xl p-6 bg-slate-900/40">
          <h2 className="text-xl font-semibold mb-3">2. Ask a Question</h2>
          <p className="text-sm text-slate-400 mb-3">
            Example: “What is the wage rate for Sheet Metal Worker?”
          </p>

          <textarea
            className="w-full p-3 rounded-lg bg-slate-800 border border-slate-700 text-sm"
            rows={3}
            placeholder="Type your question…"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          <button
            onClick={askQuestion}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium mt-3"
          >
            Ask
          </button>

          <div className="mt-4">
            {answerLoading ? (
              <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg">
                <Skeleton className="h-4 w-3/4 mb-2" />
                <Skeleton className="h-4 w-1/2" />
              </div>
            ) : (
              answer && (
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg">
                  <p className="whitespace-pre-wrap text-sm">{answer}</p>
                </div>
              )
            )}
          </div>
        </section>

        {/* ------------------------ */}
        {/* 3. Door Schedule Extraction */}
        {/* ------------------------ */}
        <section className="border border-slate-800 rounded-xl p-6 bg-slate-900/40">
          <h2 className="text-xl font-semibold mb-3">3. Door Schedule Extraction</h2>
          <p className="text-sm text-slate-400 mb-3">
            Structured extraction for door schedules (works best locally).
          </p>

          <button
            onClick={extractDoorSchedule}
            disabled={extractionLoading}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium"
          >
            {extractionLoading ? "Extracting…" : "Run Extraction"}
          </button>

          <div className="mt-4">
            {extractionLoading ? (
              <div className="p-4 bg-slate-900 border border-slate-800 rounded-lg">
                <Skeleton className="h-4 w-2/3 mb-2" />
                <Skeleton className="h-4 w-1/3" />
              </div>
            ) : (
              extraction && (
                <pre className="mt-2 p-4 bg-slate-900 border border-slate-800 rounded-lg overflow-auto max-h-80 text-xs">
                  {JSON.stringify(extraction, null, 2)}
                </pre>
              )
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
