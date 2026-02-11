import React, { useState } from 'react';

export default function KeyTermModal({ onSave, onClose }) {
  const [term, setTerm] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (term.trim()) {
      onSave(term.trim());
      setTerm('');
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl w-full max-w-md shadow-2xl">
        <header className="px-8 py-6 border-b border-slate-100 bg-slate-50/50">
          <h3 className="text-2xl font-black text-slate-900">Add Key Term</h3>
          <p className="text-slate-500 font-medium text-sm">Add a domain-specific term</p>
        </header>
        <form onSubmit={handleSubmit} className="p-8">
          <input
            type="text"
            placeholder="Enter key term"
            className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:bg-white transition-all font-medium text-slate-900"
            value={term}
            onChange={(e) => setTerm(e.target.value)}
            autoFocus
          />
          <div className="flex items-center space-x-4 pt-6">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 bg-slate-100 text-slate-600 font-bold rounded-xl hover:bg-slate-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-[2] py-3 bg-amber-600 text-white font-bold rounded-xl hover:bg-amber-700 shadow-lg shadow-amber-200 transition-all"
            >
              Add Term
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
