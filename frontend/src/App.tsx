import { useState } from 'react';
import { UploadCloud, FileText, CheckCircle, AlertTriangle, ShieldAlert, Loader2, Camera } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import BiometricModal from './components/BiometricModal';
import AddIdentityModal from './components/AddIdentityModal';
import { Database } from 'lucide-react';

interface SSEMessage {
  step: string;
  message: string;
  status: string;
  payload?: any;
  error_code?: string;
}

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<SSEMessage[]>([]);
  const [finalResult, setFinalResult] = useState<any>(null);
  const [isBioModalOpen, setIsBioModalOpen] = useState(false);
  const [isAddDbModalOpen, setIsAddDbModalOpen] = useState(false);

  const handleUpload = async (uploadedFile: File, force: boolean = false) => {
    setFile(uploadedFile);
    setProcessing(true);
    setError(null);
    setMessages([]);
    setFinalResult(null);

    const formData = new FormData();
    formData.append('file', uploadedFile);
    if (force) {
      formData.append('force', 'true');
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"}/api/v1/ocr/stream-extract`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      if (!response.body) {
        throw new Error('ReadableStream not yet supported in this browser.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        let boundary = buffer.indexOf('\n\n');
        while (boundary !== -1) {
          const chunk = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 2);
          boundary = buffer.indexOf('\n\n');
          
          const lines = chunk.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.replace('data: ', '');
              try {
                const data = JSON.parse(dataStr) as SSEMessage;
                setMessages(prev => [...prev, data]);

                if (data.status === 'FAILED') {
                  setError(data.message + (data.error_code ? ` [Code: ${data.error_code}]` : ''));
                  setProcessing(false);
                  return;
                }
                
                if (data.status === 'NEEDS_CONFIRMATION') {
                  if (window.confirm(data.message + " Click OK to force continue, or Cancel to abort.")) {
                     setProcessing(false);
                     handleUpload(uploadedFile, true);
                     return;
                  } else {
                     setError("Process aborted by user due to clarity issue.");
                     setProcessing(false);
                     return;
                  }
                }

                if (data.status === 'COMPLETED') {
                  setFinalResult(data.payload);
                  setProcessing(false);
                  return;
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e);
              }
            }
          }
        }
      }
    } catch (err: any) {
      setError(err.message || 'An error occurred during processing.');
      setProcessing(false);
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const onDragLeave = () => setIsDragging(false);
  
  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleUpload(e.dataTransfer.files[0]);
    }
  };

  const onFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleUpload(e.target.files[0]);
    }
  };



  const riskData = [
    { name: 'Risk', value: finalResult?.risk_score || 0 },
    { name: 'Safe', value: 100 - (finalResult?.risk_score || 0) }
  ];
  const riskColors = ['#EF4444', '#10B981'];

  return (
    <div className="min-h-screen p-8 flex flex-col items-center">
      <header className="w-full max-w-5xl flex justify-between items-center mb-12">
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-8 h-8 text-accent" />
            <h1 className="text-2xl font-bold tracking-tight">BorderGuard AI</h1>
          </div>
          <div className="flex space-x-4">
             <button 
               onClick={() => setIsAddDbModalOpen(true)}
               className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-lg shadow-blue-500/20"
             >
               <Database className="w-4 h-4" />
               <span>Add to Database</span>
             </button>
             <button 
               onClick={() => setIsBioModalOpen(true)}
               disabled={!finalResult?.ocr_data?.viz_data?.face_base64}
               className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-semibold transition ${finalResult?.ocr_data?.viz_data?.face_base64 ? 'bg-accent hover:bg-accent-hover text-white shadow-lg shadow-accent/20' : 'bg-white/5 text-white/30 cursor-not-allowed'}`}
             >
               <Camera className="w-4 h-4" />
               <span>Live Biometric Check</span>
             </button>
          </div>
        </header>

      <main className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Upload Column */}
        <div className="flex flex-col space-y-6">
          <div 
            className={`glass-panel p-10 flex flex-col items-center justify-center text-center transition-all duration-300 border-2 border-dashed ${isDragging ? 'border-accent bg-accent/10' : 'border-white/20'}`}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
          >
            <UploadCloud className={`w-16 h-16 mb-4 ${isDragging ? 'text-accent' : 'text-gray-400'}`} />
            <h2 className="text-xl font-semibold mb-2">Upload Document</h2>
            <p className="text-gray-400 mb-6 max-w-xs text-sm">
              {file ? `Selected: ${file.name}` : 'Drag & drop a Passport, PAN, Aadhaar, or Voter ID (JPG, PNG, PDF)'}
            </p>
            
            <input 
              type="file" 
              id="fileUpload" 
              className="hidden" 
              accept=".jpg,.jpeg,.png,.webp,.pdf"
              onChange={onFileSelect}
            />
            <label 
              htmlFor="fileUpload" 
              className="px-6 py-3 bg-accent hover:bg-blue-600 rounded-xl cursor-pointer font-medium transition-colors shadow-lg shadow-blue-500/30"
            >
              Browse Files
            </label>
          </div>

          {/* Status Stream */}
          <div className="glass-panel p-6 h-64 overflow-y-auto custom-scrollbar">
            <h3 className="font-semibold mb-4 text-gray-200">Processing Stream</h3>
            <div className="space-y-3">
              <AnimatePresence>
                {messages.map((msg, idx) => (
                  <motion.div 
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    key={idx} 
                    className="flex items-start space-x-3 text-sm"
                  >
                    {msg.status === 'FAILED' || msg.status === 'WARNING' ? (
                      <AlertTriangle className={`w-4 h-4 mt-0.5 ${msg.status === 'FAILED' ? 'text-danger' : 'text-orange-500'}`} />
                    ) : (idx === messages.length - 1 && processing) ? (
                      <Loader2 className="w-4 h-4 text-accent animate-spin mt-0.5" />
                    ) : (
                      <CheckCircle className="w-4 h-4 text-success mt-0.5" />
                    )}
                    
                    <div>
                      <span className="font-medium text-gray-300">{msg.step}: </span>
                      <span className={msg.status === 'FAILED' ? 'text-danger' : (msg.status === 'WARNING' ? 'text-orange-500' : 'text-gray-400')}>{msg.message}</span>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              {messages.length === 0 && !processing && (
                <p className="text-sm text-gray-500 italic">Upload a document to view logs...</p>
              )}
            </div>
          </div>
        </div>

        {/* Column 2: OCR Extraction Results */}
        <div className="flex flex-col space-y-6">
          {error && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-panel border-danger/50 bg-danger/10 p-6 flex items-start space-x-4"
            >
              <AlertTriangle className="w-6 h-6 text-danger shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold text-danger mb-1">Verification Rejected</h3>
                <p className="text-sm text-gray-300">{error}</p>
              </div>
            </motion.div>
          )}

          {finalResult && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-panel p-6 space-y-6 flex flex-col h-full"
            >
              <div className="flex justify-between items-center border-b border-white/10 pb-4">
                <h3 className="text-xl font-semibold flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-accent" />
                  Detected: <span className="ml-2 text-accent bg-accent/20 px-3 py-1 rounded-full text-sm">{finalResult.doc_type}</span>
                </h3>
              </div>

              <div className="space-y-4 flex-grow">
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Document Number</p>
                  <p className="font-mono text-lg">{finalResult.ocr_data?.viz_data?.doc_number || finalResult.ocr_data?.mrz_data?.document_number || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Name</p>
                  <p className="font-medium text-lg">{finalResult.ocr_data?.mrz_data?.names || finalResult.ocr_data?.viz_data?.name || 'N/A'}</p>
                </div>

                <div className="mt-4 p-4 bg-black/30 rounded-lg border border-white/5">
                   <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">Address</p>
                   <p className="text-sm text-gray-300">{finalResult.ocr_data?.viz_data?.address || 'N/A'}</p>
                </div>

                {finalResult.ocr_data?.viz_data?.face_base64 && (
                  <div className="mt-4 flex flex-col items-center p-4 bg-black/30 rounded-lg border border-white/5">
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Extracted Photo</p>
                    <img 
                      src={`data:image/jpeg;base64,${finalResult.ocr_data.viz_data.face_base64}`} 
                      alt="Cropped Face" 
                      className="w-32 h-32 object-cover rounded-full border-4 border-accent shadow-lg shadow-accent/20"
                    />
                  </div>
                )}
                
                {finalResult.ocr_data?.raw_mrz_lines && finalResult.ocr_data.raw_mrz_lines.length > 0 && (
                  <div className="mt-6 pt-4 border-t border-white/10">
                    <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Extracted MRZ</p>
                    <div className="bg-black/50 p-3 rounded-lg font-mono text-sm text-green-400 whitespace-pre-wrap break-all shadow-inner border border-white/5">
                      {finalResult.ocr_data.raw_mrz_lines.join('\n')}
                    </div>
                    {finalResult.ocr_data.mrz_data && (
                      <div className="mt-2 text-xs">
                        {finalResult.ocr_data.mrz_data.mrz_checksum_valid ? (
                           <span className="text-success flex items-center"><CheckCircle className="w-3 h-3 mr-1"/> Checksums Valid</span>
                        ) : (
                           <span className="text-danger flex items-center"><AlertTriangle className="w-3 h-3 mr-1"/> Checksum Failed!</span>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>

              {finalResult.ocr_data?.viz_data?.face_base64 && (
                <div className="mt-6 pt-4 border-t border-white/10 flex justify-center mt-auto">
                  <button 
                    onClick={() => setIsBioModalOpen(true)}
                    className="px-6 py-3 bg-accent hover:bg-blue-600 text-white font-bold rounded-lg shadow-lg flex items-center transition-colors w-full justify-center"
                  >
                    <Camera className="w-5 h-5 mr-2" />
                    Verify Liveness & Identity
                  </button>
                </div>
              )}
            </motion.div>
          )}

          {!finalResult && !error && (
            <div className="glass-panel p-10 flex flex-col items-center justify-center h-full text-gray-500 min-h-[400px]">
              <FileText className="w-12 h-12 mb-4 opacity-20" />
              <p>Upload a document to view OCR extraction</p>
            </div>
          )}
        </div>

        {/* Column 3: Forensic & Tamper Analysis */}
        <div className="flex flex-col space-y-6">
          {finalResult && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-panel p-6 space-y-6"
            >
              <div className="flex justify-between items-center border-b border-white/10 pb-4">
                <h3 className="text-xl font-semibold flex items-center">
                  <ShieldAlert className="w-5 h-5 mr-2 text-accent" />
                  Forensic Analysis
                </h3>
              </div>

              <div className="h-40 relative flex flex-col items-center justify-center mb-6">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskData}
                      innerRadius={35}
                      outerRadius={65}
                      startAngle={180}
                      endAngle={0}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {riskData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={riskColors[index % riskColors.length]} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-0 flex items-center justify-center pt-8">
                  <span className="text-3xl font-bold">{finalResult.risk_score || 0}%</span>
                </div>
                <span className="text-xs text-gray-500 mt-2 font-bold uppercase tracking-widest">Overall Risk</span>
              </div>

              {finalResult.tamper_data?.needs_review && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mt-4 p-5 rounded-lg bg-red-900/40 border border-red-500/50 flex flex-col items-center justify-center text-center shadow-[0_0_15px_rgba(239,68,68,0.3)]"
                >
                   <AlertTriangle className="w-8 h-8 text-red-500 mb-2 animate-pulse" />
                   <h4 className="text-red-400 font-bold text-lg tracking-wide uppercase">Manual Review Required</h4>
                   <p className="text-xs text-red-300 mt-1 max-w-sm">Suspicious patterns detected. Likely physical or digital tampering.</p>
                </motion.div>
              )}

              {finalResult.ocr_data?.qr_data && (
                <div className="mt-4 p-4 bg-black/30 rounded-lg border border-white/5">
                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-2 flex items-center">
                    <ShieldAlert className="w-4 h-4 mr-2" />
                    QR Code Payload Verification
                  </p>
                  <pre className={`p-3 rounded-lg font-mono text-[10px] whitespace-pre-wrap shadow-inner border border-white/5 overflow-x-auto ${finalResult.ocr_data.qr_data.error ? 'text-danger bg-danger/10 border-danger/30' : 'text-green-400 bg-black/50'}`}>
                    {JSON.stringify(finalResult.ocr_data.qr_data, null, 2)}
                  </pre>
                </div>
              )}

              {finalResult.tamper_data?.db_verification_status && (
                 <div className={`mt-4 p-4 rounded-lg border ${finalResult.tamper_data.db_verification_status === 'VERIFIED' ? 'bg-success/10 border-success/50 text-success' : 'bg-danger/10 border-danger/50 text-danger'}`}>
                   <p className="text-xs uppercase tracking-wider mb-2 flex items-center font-bold">
                     <Database className="w-4 h-4 mr-2" />
                     National Database Check (O(log N) Indexed): {finalResult.tamper_data.db_verification_status}
                   </p>
                   <p className="text-[11px] opacity-90">{finalResult.tamper_data.db_verification_message}</p>
                 </div>
              )}

              {finalResult.tamper_data?.format_validation_status && (
                 <div className={`mt-4 p-4 rounded-lg border ${finalResult.tamper_data.format_validation_status === 'PASSED' ? 'bg-blue-900/20 border-blue-500/50 text-blue-400' : 'bg-danger/10 border-danger/50 text-danger'}`}>
                   <p className="text-xs uppercase tracking-wider mb-2 flex items-center font-bold">
                     Format Check: {finalResult.tamper_data.format_validation_status}
                   </p>
                   <p className="text-[11px] opacity-90">{finalResult.tamper_data.format_validation_message}</p>
                 </div>
              )}

              {finalResult.tamper_data?.layers && (
                <div className="mt-4 grid grid-cols-4 gap-2">
                   <div className="p-3 bg-black/30 rounded-lg border border-white/5 text-center flex flex-col justify-between">
                      <p className="text-[9px] text-gray-500 uppercase tracking-wider mb-1 line-clamp-2 leading-tight">Recapture Risk</p>
                      <p className="font-mono text-sm text-red-400">{finalResult.tamper_data.layers.moire?.risk_score?.toFixed(1) || 0}%</p>
                   </div>
                   <div className="p-3 bg-black/30 rounded-lg border border-white/5 text-center flex flex-col justify-between">
                      <p className="text-[9px] text-gray-500 uppercase tracking-wider mb-1 line-clamp-2 leading-tight">Noise Risk</p>
                      <p className="font-mono text-sm text-yellow-400">{finalResult.tamper_data.layers.noise?.risk_score?.toFixed(1) || 0}%</p>
                   </div>
                   <div className="p-3 bg-black/30 rounded-lg border border-white/5 text-center flex flex-col justify-between">
                      <p className="text-[9px] text-gray-500 uppercase tracking-wider mb-1 line-clamp-2 leading-tight">SIFT Clones</p>
                      <p className="font-mono text-sm text-blue-400">{finalResult.tamper_data.layers.sift?.matches_found || 0}</p>
                   </div>
                   <div className="p-3 bg-black/30 rounded-lg border border-white/5 text-center flex flex-col justify-between overflow-hidden">
                      <p className="text-[9px] text-gray-500 uppercase tracking-wider mb-1 line-clamp-2 leading-tight">EXIF Tool</p>
                      <p className="font-mono text-[10px] text-purple-400 truncate" title={finalResult.tamper_data.layers.metadata?.software || 'None'}>
                        {finalResult.tamper_data.layers.metadata?.software || 'None'}
                      </p>
                   </div>
                </div>
              )}

              {finalResult.tamper_data?.vertex_ai?.forensic_analysis && (
                <div className={`mt-4 p-4 rounded-lg border ${finalResult.tamper_data.vertex_ai.forensic_analysis.is_tampered ? 'bg-danger/10 border-danger/50 text-danger' : 'bg-success/10 border-success/50 text-success'}`}>
                  <p className="text-xs uppercase tracking-wider mb-2 flex items-center font-bold">
                    Vertex AI CNN: {finalResult.tamper_data.vertex_ai.forensic_analysis.is_tampered ? 'TAMPERING DETECTED' : 'AUTHENTIC'}
                  </p>
                  <p className="text-[11px] opacity-90 whitespace-pre-wrap leading-relaxed">{finalResult.tamper_data.vertex_ai.forensic_analysis.reasoning}</p>
                </div>
              )}

              {finalResult.tamper_data?.layers?.ela?.heatmap_base64 && (
                <div className="mt-4 flex flex-col p-4 bg-black/30 rounded-lg border border-white/5">
                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-3 flex items-center"><ShieldAlert className="w-4 h-4 mr-2" /> ELA Heatmap Analysis</p>
                  <img 
                    src={`data:image/jpeg;base64,${finalResult.tamper_data.layers.ela.heatmap_base64}`} 
                    alt="ELA Heatmap" 
                    className="w-full object-contain rounded border border-white/10"
                  />
                  <p className="text-[10px] text-gray-400 mt-2">Bright spots indicate different compression levels, typical of "photo-in-photo" splicing or copy-paste edits.</p>
                </div>
              )}
            </motion.div>
          )}

          {!finalResult && !error && (
            <div className="glass-panel p-10 flex flex-col items-center justify-center h-full text-gray-500 min-h-[400px]">
              <ShieldAlert className="w-12 h-12 mb-4 opacity-20" />
              <p>Forensic Analysis will appear here</p>
            </div>
          )}
        </div>
        
      </main>

      <BiometricModal 
        isOpen={isBioModalOpen} 
        onClose={() => setIsBioModalOpen(false)} 
        docFaceB64={finalResult?.ocr_data?.viz_data?.face_base64 || ''} 
      />
      
      <AddIdentityModal
        isOpen={isAddDbModalOpen}
        onClose={() => setIsAddDbModalOpen(false)}
      />
    </div>
  );
}
