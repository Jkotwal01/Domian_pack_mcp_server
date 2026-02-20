import React, { useState } from 'react';

export default function EntityModal({ entity, onSave, onClose }) {
  const [formData, setFormData] = useState(entity || {
    name: '',
    type: '',
    description: '',
    attributes: [],
    synonyms: []
  });
  const [newAttribute, setNewAttribute] = useState({ name: '', description: '' });
  const [newSynonym, setNewSynonym] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  const addAttribute = () => {
    if (newAttribute.name.trim()) {
      setFormData({
        ...formData,
        attributes: [...(formData.attributes || []), newAttribute]
      });
      setNewAttribute({ name: '', description: '' });
    }
  };

  const removeAttribute = (index) => {
    setFormData({
      ...formData,
      attributes: formData.attributes.filter((_, i) => i !== index)
    });
  };

  const addSynonym = () => {
    if (newSynonym.trim()) {
      setFormData({
        ...formData,
        synonyms: [...(formData.synonyms || []), newSynonym.trim()]
      });
      setNewSynonym('');
    }
  };

  const removeSynonym = (index) => {
    setFormData({
      ...formData,
      synonyms: formData.synonyms.filter((_, i) => i !== index)
    });
  };

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-6 overflow-y-auto">
      <div className="bg-white rounded-2xl w-full max-w-2xl shadow-2xl my-8">
        <header className="px-8 py-6 border-b border-slate-100 bg-slate-50/50">
          <h3 className="text-2xl font-black text-slate-900">{entity ? 'Edit Entity' : 'Add New Entity'}</h3>
          <p className="text-slate-500 font-medium text-sm">Define the entity properties and attributes</p>
        </header>
        <form onSubmit={handleSubmit} className="p-8 space-y-6 max-h-[70vh] overflow-y-auto">
          {/* Name */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Entity Name *</label>
              <span className="text-[10px] font-bold text-slate-400">Use Title Case</span>
            </div>
            <input
              type="text"
              required
              placeholder="e.g. Legal Issue, Court Case, Medical Record"
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:bg-white transition-all font-medium text-slate-900"
              value={formData.name}
              onChange={(e) => {
                const newName = e.target.value;
                const newType = newName.trim().toUpperCase().replace(/\s+/g, '_');
                setFormData({ ...formData, name: newName, type: newType });
              }}
            />
          </div>

          {/* Type */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Entity Type</label>
              <span className="text-[10px] font-bold text-blue-500">Auto-generated from name</span>
            </div>
            <input
              type="text"
              placeholder="e.g. LEGAL_ISSUE, COURT_CASE"
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:bg-white transition-all font-mono text-sm text-slate-500 bg-slate-50/50"
              value={formData.type || ''}
              onChange={(e) => setFormData({ ...formData, type: e.target.value.toUpperCase().replace(/\s+/g, '_') })}
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Description</label>
            <textarea
              rows="3"
              placeholder="Describe what this entity represents..."
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:bg-white transition-all font-medium text-slate-900 resize-none"
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>

          {/* Attributes */}
          <div className="space-y-3">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Attributes</label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Attribute name"
                className="flex-1 px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-sm"
                value={newAttribute.name}
                onChange={(e) => setNewAttribute({ ...newAttribute, name: e.target.value })}
              />
              <input
                type="text"
                placeholder="Description (optional)"
                className="flex-1 px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-sm"
                value={newAttribute.description}
                onChange={(e) => setNewAttribute({ ...newAttribute, description: e.target.value })}
              />
              <button
                type="button"
                onClick={addAttribute}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-bold"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {formData.attributes?.map((attr, idx) => (
                <span key={idx} className="px-3 py-1 bg-blue-50 text-blue-600 rounded-lg text-xs font-bold border border-blue-100 flex items-center gap-2">
                  {typeof attr === 'string' ? attr : attr.name}
                  <button
                    type="button"
                    onClick={() => removeAttribute(idx)}
                    className="hover:text-red-600"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Synonyms */}
          <div className="space-y-3">
            <label className="text-xs font-black text-slate-400 uppercase tracking-widest">Synonyms</label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Add synonym"
                className="flex-1 px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-sm"
                value={newSynonym}
                onChange={(e) => setNewSynonym(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSynonym())}
              />
              <button
                type="button"
                onClick={addSynonym}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-bold"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {formData.synonyms?.map((syn, idx) => (
                <span key={idx} className="px-3 py-1 bg-purple-50 text-purple-600 rounded-lg text-xs font-bold border border-purple-100 flex items-center gap-2">
                  {syn}
                  <button
                    type="button"
                    onClick={() => removeSynonym(idx)}
                    className="hover:text-red-600"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Actions */}
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
              className="flex-[2] py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all"
            >
              {entity ? 'Save Changes' : 'Add Entity'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
