import { useRef, useState, useEffect } from 'react';
import { Camera, ShieldCheck, XCircle, Loader2, AlertTriangle } from 'lucide-react';

interface BiometricModalProps {
  isOpen: boolean;
  onClose: () => void;
  docFaceB64: string;
}

export default function BiometricModal({ isOpen, onClose, docFaceB64 }: BiometricModalProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  
  const [isStreaming, setIsStreaming] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [liveFeedback, setLiveFeedback] = useState('Initializing Camera...');
  const [eyeLandmarks, setEyeLandmarks] = useState<{x: number, y: number}[]>([]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: 640, height: 480 }, audio: false });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setLiveFeedback('Ready to scan. Press "Start Live Verification".');
    } catch {
      setError("Failed to access camera. Please allow permissions.");
      setLiveFeedback('');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(t => t.stop());
    }
  };

  const handleStartCapture = () => {
    if (!videoRef.current || !videoRef.current.srcObject) return;
    setError('');
    setResult(null);
    setIsStreaming(true);
    setLiveFeedback('Connecting to Secure Biometric Socket...');
    
    // Open WebSocket
    const ws = new WebSocket(`${import.meta.env.VITE_WS_URL || "ws://127.0.0.1:8000"}/api/v1/bio/ws/verify`);
    wsRef.current = ws;

    ws.onopen = () => {
      // Send initial face config
      ws.send(JSON.stringify({ doc_face_b64: docFaceB64 }));
      setLiveFeedback('Connected. Analyzing Face Mesh...');
      startFrameLoop();
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.status === 'processing') {
        setLiveFeedback(data.message);
        if (data.eye_landmarks) {
          setEyeLandmarks(data.eye_landmarks);
        }
      } else if (data.status === 'completed') {
        setResult(data.result);
        stopStreaming();
      } else if (data.status === 'FAILED') {
        setError(data.message);
        stopStreaming();
      }
    };

    ws.onerror = () => {
      setError("WebSocket connection failed.");
      stopStreaming();
    };

    ws.onclose = () => {
      stopStreaming();
    };
  };

  const startFrameLoop = () => {
    const sendFrame = () => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
      if (!videoRef.current || !canvasRef.current) return;

      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      
      if (ctx && video.videoWidth > 0) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Encode at low quality for ultra-fast streaming
        const frameData = canvas.toDataURL('image/jpeg', 0.5);
        wsRef.current.send(JSON.stringify({ frame: frameData }));
      }
      
      // Throttle to roughly 10 FPS for optimal network performance
      setTimeout(() => {
        animationFrameRef.current = requestAnimationFrame(sendFrame);
      }, 100);
    };
    
    animationFrameRef.current = requestAnimationFrame(sendFrame);
  };

  const stopStreaming = () => {
    setIsStreaming(false);
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (wsRef.current) {
      if (wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
      wsRef.current = null;
    }
  };

  const handleRetry = () => {
    stopStreaming();
    setResult(null);
    setError('');
    setLiveFeedback('Ready to scan. Press "Start Live Verification".');
    setEyeLandmarks([]);
  };

  useEffect(() => {
    if (isOpen) {
      startCamera();
    } else {
      stopCamera();
      stopStreaming();
    }
    return () => {
      stopCamera();
      stopStreaming();
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="glass-panel p-8 max-w-4xl w-full relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-white">
          <XCircle className="w-6 h-6" />
        </button>

        <h2 className="text-xl font-bold flex items-center mb-6">
          <Camera className="w-6 h-6 mr-3 text-accent" />
          Live Biometric Verification
        </h2>

        {/* Hidden canvas for extracting frames */}
        <canvas ref={canvasRef} className="hidden" />

        {!result && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {/* Left: Original Document Face */}
                <div className="flex flex-col items-center">
                    <h3 className="text-sm text-gray-400 font-medium mb-3 uppercase tracking-wide">Document Photo</h3>
                    <div className="w-full aspect-video bg-black/40 rounded-lg overflow-hidden border border-white/10 relative flex items-center justify-center">
                        <img src={`data:image/jpeg;base64,${docFaceB64}`} alt="Extracted Face" className="h-full object-contain" />
                    </div>
                </div>

                {/* Right: Live Camera Feed */}
                <div className="flex flex-col items-center">
                    <h3 className="text-sm text-gray-400 font-medium mb-3 uppercase tracking-wide">Live Camera</h3>
                    <div className="w-full aspect-video bg-black rounded-lg overflow-hidden border border-white/10 relative">
                        <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover transform -scale-x-100" />
                        
                        {/* Eye tracking dots overlay */}
                        {eyeLandmarks.map((point, idx) => (
                            <div 
                                key={idx}
                                className="absolute w-1.5 h-1.5 bg-green-400 rounded-full shadow-[0_0_5px_#4ade80]"
                                style={{
                                    left: `${(1.0 - point.x) * 100}%`,
                                    top: `${point.y * 100}%`,
                                    transform: 'translate(-50%, -50%)'
                                }}
                            />
                        ))}
                        
                        <div className="absolute inset-0 border-4 border-dashed border-white/20 rounded-lg pointer-events-none flex items-center justify-center">
                            {!isStreaming && <span className="text-white/50 text-sm font-medium bg-black/50 px-3 py-1 rounded">Position face inside frame</span>}
                        </div>
                        
                        {isStreaming && (
                            <div className="absolute top-4 right-4 flex items-center space-x-2 bg-red-500/20 px-3 py-1 rounded-full border border-red-500/50">
                            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                            <span className="text-red-500 text-sm font-bold">LIVE STREAM</span>
                            </div>
                        )}

                        {liveFeedback && (
                            <div className="absolute bottom-4 left-4 right-4 text-center">
                              <span className="bg-black/70 text-white text-sm font-medium px-4 py-2 rounded-full inline-flex items-center backdrop-blur-md border border-white/10">
                                {isStreaming && <Loader2 className="w-4 h-4 mr-2 animate-spin text-accent" />}
                                {liveFeedback}
                              </span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        )}

        {result && (
            <div className="mb-6 space-y-4">
                <div className={`p-4 border rounded flex items-center space-x-3 ${result.liveness_status === 'PASSED' ? 'bg-success/10 border-success/50' : 'bg-danger/10 border-danger/50'}`}>
                    {result.liveness_status === 'PASSED' ? <ShieldCheck className="w-8 h-8 text-success shrink-0" /> : <AlertTriangle className="w-8 h-8 text-danger shrink-0" />}
                    <div>
                        <h3 className={`font-bold ${result.liveness_status === 'PASSED' ? 'text-success' : 'text-danger'}`}>
                            {result.liveness_status === 'PASSED' ? 'VERIFICATION SUCCESSFUL' : 'VERIFICATION FAILED'}
                        </h3>
                        <p className="text-sm opacity-80 text-wrap break-all">Reason: {result.liveness_status.replace(/_/g, ' ')}</p>
                    </div>
                </div>
                <div className="p-4 bg-black/40 rounded border border-white/10 flex justify-between items-center">
                    <span className="text-sm text-gray-400">DeepFace Confidence Score</span>
                    <span className={`font-mono text-xl ${result.similarity_score > 70 ? 'text-success' : 'text-danger'}`}>
                        {result.similarity_score.toFixed(1)}%
                    </span>
                </div>
            </div>
        )}

        {error && <p className="text-danger text-sm text-center mb-4">{error}</p>}

        <div className="text-center flex space-x-4">
          {!result ? (
              <>
                  <button 
                    onClick={isStreaming ? handleRetry : handleStartCapture} 
                    className={`px-6 py-3 font-bold rounded-lg shadow-lg transition-all w-full flex justify-center items-center ${isStreaming ? 'bg-red-500 hover:bg-red-600 text-white shadow-red-500/30' : 'bg-accent hover:bg-blue-600 text-white shadow-blue-500/30'}`}
                >
                    {isStreaming ? "Stop & Retry" : "Start Live Verification"}
                </button>
              </>
          ) : (
              <>
                  <button 
                      onClick={handleRetry} 
                      className="px-6 py-3 bg-accent hover:bg-blue-600 text-white font-bold rounded-lg w-full transition-colors"
                  >
                      Retry Verification
                  </button>
                  <button onClick={onClose} className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg w-full transition-colors">
                      Close
                  </button>
              </>
          )}
        </div>
      </div>
    </div>
  );
}
