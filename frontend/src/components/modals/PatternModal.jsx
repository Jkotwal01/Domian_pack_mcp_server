import React, { useState } from 'react';

export default function PatternModal({ pattern, entities, onSave, onClose }) {
  const [formData, setFormData] = useState(pattern || {
    pattern: '',
    entity_type: '',
    attribute: '',
    confidence: 0.9,
    extract_full_match: true
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl w-full max-w-2xl shadow-2xl">
        <header className="px-8 py-6 border-b border-slate-100 bg-slate-50/50">
          <h3 className="text-2xl font-black text-slate-900">{pattern ? 'Edit Extraction Pattern' : 'Add New Extraction Pattern'}</h3>
          <p className="text-slate-500 font-medium text-sm">Define a regex pattern to extract data</p>
        </header>
        <form onSubmit={handleSubmit} className="p-8 space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Regex Pattern *</label>
            <input
              type="text"
              required
              placeholder="e.g. \b\d{1,2}/\d{1,2}/\d{4}\b"
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:bg-white transition-all font-mono text-sm text-slate-900"
              value={formData.pattern}
              onChange={(e) => setFormData({ ...formData, pattern: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Entity Type *</label>
              <select
                required
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:bg-white transition-all font-medium text-slate-900"
                value={formData.entity_type}
                onChange={(e) => setFormData({ ...formData, entity_type: e.target.value })}
              >
                <option value="">Select entity</option>
                {entities.map((entity, idx) => (
                  <option key={idx} value={entity.name}>{entity.name}</option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Attribute *</label>
              <input
                type="text"
                required
                placeholder="e.g. effective_date"
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:bg-white transition-all font-medium text-slate-900"
                value={formData.attribute}
                onChange={(e) => setFormData({ ...formData, attribute: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Confidence Level: {(formData.confidence * 100).toFixed(0)}%</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              className="w-full"
              value={formData.confidence}
              onChange={(e) => setFormData({ ...formData, confidence: parseFloat(e.target.value) })}
            />
          </div>

          <div className="flex items-center space-x-4 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 bg-slate-100 text-slate-600 font-bold rounded-xl hover:bg-slate-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-[2] py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 shadow-lg shadow-emerald-200 transition-all"
            >
              {pattern ? 'Save Changes' : 'Add Pattern'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
