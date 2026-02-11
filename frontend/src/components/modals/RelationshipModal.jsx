import React, { useState } from 'react';

export default function RelationshipModal({ relationship, entities, onSave, onClose }) {
  const [formData, setFormData] = useState(relationship || {
    name: '',
    from: '',
    to: '',
    description: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-6">
      <div className="bg-white rounded-2xl w-full max-w-2xl shadow-2xl">
        <header className="px-8 py-6 border-b border-slate-100 bg-slate-50/50">
          <h3 className="text-2xl font-black text-slate-900">{relationship ? 'Edit Relationship' : 'Add New Relationship'}</h3>
          <p className="text-slate-500 font-medium text-sm">Define how entities relate to each other</p>
        </header>
        <form onSubmit={handleSubmit} className="p-8 space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Relationship Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. SIGNS, CONTAINS, HAS_DIAGNOSIS"
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:bg-white transition-all font-medium text-slate-900"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest">From Entity *</label>
              <select
                required
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:bg-white transition-all font-medium text-slate-900"
                value={formData.from}
                onChange={(e) => setFormData({ ...formData, from: e.target.value })}
              >
                <option value="">Select entity</option>
                {entities.map((entity, idx) => (
                  <option key={idx} value={entity.name}>{entity.name}</option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest">To Entity *</label>
              <select
                required
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:bg-white transition-all font-medium text-slate-900"
                value={formData.to}
                onChange={(e) => setFormData({ ...formData, to: e.target.value })}
              >
                <option value="">Select entity</option>
                {entities.map((entity, idx) => (
                  <option key={idx} value={entity.name}>{entity.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Description</label>
            <textarea
              rows="3"
              placeholder="Describe the relationship..."
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:bg-white transition-all font-medium text-slate-900 resize-none"
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
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
              className="flex-[2] py-3 bg-purple-600 text-white font-bold rounded-xl hover:bg-purple-700 shadow-lg shadow-purple-200 transition-all"
            >
              {relationship ? 'Save Changes' : 'Add Relationship'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
