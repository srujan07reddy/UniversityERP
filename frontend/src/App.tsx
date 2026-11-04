import React from 'react';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-brand-ivory text-brand-charcoal flex flex-col justify-center items-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-sm border border-slate-100 p-8 text-center space-y-4">
        <div className="w-16 h-16 rounded-2xl bg-brand-emerald text-brand-gold flex items-center justify-center mx-auto text-2xl font-bold">
          JU
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-brand-charcoal">
          Jeppiaar University ERP
        </h1>
        <p className="text-sm text-slate-500">
          Unified Institutional Platform (Web & Mobile Native Android APK)
        </p>
        <div className="pt-4 border-t border-slate-100 text-xs text-slate-400">
          Version 1.0 • Ready for Web & Capacitor Native Build
        </div>
      </div>
    </div>
  );
};

export default App;
