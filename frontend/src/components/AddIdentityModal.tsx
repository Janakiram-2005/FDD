import React, { useState } from 'react';
import { XCircle, Loader2, Database } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function AddIdentityModal({ isOpen, onClose }: Props) {
  const [docType, setDocType] = useState('AADHAAR');
  const [docNumber, setDocNumber] = useState('');
  const [name, setName] = useState('');
  const [dob, setDob] = useState('');
  const [isBlacklisted, setIsBlacklisted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"}/api/v1/db/add-identity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doc_type: docType,
          doc_number: docNumber,
          name: name,
          dob: dob,
          is_blacklisted: isBlacklisted,
          notes: "Added dynamically via UI"
        })
      });
      const data = await response.json();
      setMessage(data.message || 'Identity added successfully!');
      setTimeout(() => {
        onClose();
        setMessage('');
        setDocNumber('');
        setName('');
        setDob('');
      }, 2000);
    } catch (err: any) {
      setMessage('Failed to connect to database.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="glass-panel p-8 max-w-md w-full relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-white">
          <XCircle className="w-6 h-6" />
        </button>
        <h2 className="text-2xl font-bold mb-2 flex items-center">
          <Database className="w-6 h-6 mr-2 text-blue-400" />
          Add to National DB
        </h2>
        <p className="text-sm text-gray-400 mb-6">
          Insert new identities here. Thanks to MongoDB B-Tree indexing, verifying against millions of records takes just O(log N) time (~5ms)!
        </p>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-500 mb-1">Doc Type</label>
            <select value={docType} onChange={e => setDocType(e.target.value)} className="w-full bg-black/50 border border-white/10 rounded p-2 text-white">
              <option value="AADHAAR">Aadhaar Card</option>
              <option value="PAN">PAN Card</option>
              <option value="VOTER_ID">Voter ID</option>
              <option value="PASSPORT">Passport</option>
            </select>
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-500 mb-1">Doc Number</label>
            <input required type="text" value={docNumber} onChange={e => setDocNumber(e.target.value)} className="w-full bg-black/50 border border-white/10 rounded p-2 text-white" placeholder="e.g. ABCDE1234F" />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-500 mb-1">Full Name</label>
            <input required type="text" value={name} onChange={e => setName(e.target.value)} className="w-full bg-black/50 border border-white/10 rounded p-2 text-white" placeholder="e.g. Vikram Singh" />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wider text-gray-500 mb-1">Date of Birth</label>
            <input type="text" value={dob} onChange={e => setDob(e.target.value)} className="w-full bg-black/50 border border-white/10 rounded p-2 text-white" placeholder="DD/MM/YYYY" />
          </div>
          <div className="flex items-center">
            <input type="checkbox" checked={isBlacklisted} onChange={e => setIsBlacklisted(e.target.checked)} className="mr-2" />
            <label className="text-sm text-red-400 font-bold">Mark as Blacklisted / Fraudulent</label>
          </div>
          
          <button disabled={loading} type="submit" className="w-full mt-4 btn-primary flex justify-center items-center py-3">
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Save to Database'}
          </button>
          
          {message && <p className="text-center text-sm text-green-400 mt-2">{message}</p>}
        </form>
      </div>
    </div>
  );
}
