const { useState, useEffect, useRef } = React;

// --- Components ---

const Sidebar = () => (
    <aside className="w-64 glass-panel h-screen flex flex-col p-4 z-10">
        <div className="flex items-center gap-3 px-2 mb-10">
            <div className="w-8 h-8 bg-brand-primary rounded-lg flex items-center justify-center">
                <i className="fas fa-microchip text-white text-sm"></i>
            </div>
            <h1 className="font-display font-bold text-lg tracking-tight">SRE Commander</h1>
        </div>
        
        <nav className="flex-1 space-y-1">
            <div className="sidebar-link active">
                <i className="fas fa-columns"></i>
                <span>Dashboard</span>
            </div>
            <div className="sidebar-link">
                <i className="fas fa-list-ul"></i>
                <span>Incidents</span>
            </div>
            <div className="sidebar-link">
                <i className="fas fa-database"></i>
                <span>KEDB</span>
            </div>
            <div className="sidebar-link">
                <i className="fas fa-chart-pie"></i>
                <span>Analytics</span>
            </div>
        </nav>

        <div className="mt-auto border-t border-white/5 pt-4">
            <div className="sidebar-link group">
                <i className="fas fa-cog group-hover:rotate-90 transition-transform"></i>
                <span>Settings</span>
            </div>
            <div className="mt-4 px-2 py-3 rounded-xl bg-slate-950/50 border border-white/5">
                <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-2">System Health</div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span className="text-xs text-slate-300">Clusters Operational</span>
                </div>
            </div>
        </div>
    </aside>
);

const Navbar = () => (
    <header className="h-16 border-b border-white/5 px-8 flex items-center justify-between">
        <div className="flex items-center gap-4">
            <div className="text-xs font-bold text-slate-500 uppercase tracking-widest">Environment:</div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                PRODUCTION
            </div>
        </div>
        <div className="flex items-center gap-6">
            <div className="text-right">
                <div className="text-sm font-semibold text-white">SRE Lead</div>
                <div className="text-[10px] text-slate-500">Cloud Operations</div>
            </div>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-brand-primary to-brand-secondary p-[1px]">
                <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center border border-white/10">
                    <i className="fas fa-user-shield text-brand-primary"></i>
                </div>
            </div>
        </div>
    </header>
);

const SkeletonCard = () => (
    <div className="glass-panel p-6 space-y-4">
        <div className="skeleton h-6 w-1/3"></div>
        <div className="skeleton h-24 w-full"></div>
        <div className="flex gap-4">
            <div className="skeleton h-8 w-1/4"></div>
            <div className="skeleton h-8 w-1/4"></div>
        </div>
    </div>
);

const ResultsPanel = ({ data, loading }) => {
    if (loading) return (
        <div className="space-y-6 animate-pulse">
            <SkeletonCard />
            <div className="grid grid-cols-2 gap-6">
                <SkeletonCard />
                <SkeletonCard />
            </div>
        </div>
    );

    if (!data) return (
        <div className="h-full flex flex-col items-center justify-center text-center p-12 opacity-50">
            <div className="w-24 h-24 mb-6 rounded-3xl bg-slate-900 border border-white/5 flex items-center justify-center text-4xl text-slate-700">
                <i className="fas fa-terminal"></i>
            </div>
            <h3 className="text-xl font-display font-medium text-slate-400 mb-2">No active analysis</h3>
            <p className="max-w-xs text-sm text-slate-500 leading-relaxed">Paste incident logs or symptoms above to begin AI-powered diagnostic correlation.</p>
        </div>
    );

    const sourceColors = {
        'KEDB': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
        'VECTOR DB': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
        'LLM_FALLBACK': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
        'fallback': 'bg-purple-500/10 text-purple-400 border-purple-500/20'
    };

    const generatePDF = () => {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        // Brand Header
        doc.setFillColor(15, 23, 42); // slate-900
        doc.rect(0, 0, 210, 40, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(22);
        doc.setFont("helvetica", "bold");
        doc.text("SRE COMMANDER", 20, 20);
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");
        doc.text("AI-POWERED INCIDENT INTELLIGENCE REPORT", 20, 30);
        doc.text(`DATE: ${new Date().toLocaleString()}`, 140, 30);

        // Incident Summary
        doc.setTextColor(15, 23, 42);
        doc.setFontSize(14);
        doc.setFont("helvetica", "bold");
        doc.text("INCIDENT SUMMARY", 20, 55);
        doc.setFontSize(11);
        doc.setFont("helvetica", "italic");
        const summaryLines = doc.splitTextToSize(`"${data.summary}"`, 170);
        doc.text(summaryLines, 20, 65);

        // Metrics Table
        doc.autoTable({
            startY: 85,
            head: [['METRIC', 'VALUE']],
            body: [
                ['SEVERITY', data.severity],
                ['COMPLEXITY', data.complexity?.toUpperCase()],
                ['CONFIDENCE', data.confidence],
                ['SOURCE', data.source]
            ],
            theme: 'grid',
            headStyles: { fillColor: [59, 130, 246] }
        });

        // Diagnostic Findings
        doc.setFontSize(14);
        doc.setFont("helvetica", "bold");
        doc.text("DIAGNOSTIC FINDINGS", 20, doc.lastAutoTable.finalY + 15);
        doc.setFontSize(11);
        doc.setFont("helvetica", "bold");
        doc.text("Confirmed Root Cause:", 20, doc.lastAutoTable.finalY + 25);
        doc.setFont("helvetica", "normal");
        const causeLines = doc.splitTextToSize(data.root_cause, 170);
        doc.text(causeLines, 20, doc.lastAutoTable.finalY + 32);

        // Resolution Steps Table
        doc.autoTable({
            startY: doc.lastAutoTable.finalY + 50,
            head: [['#', 'RESOLUTION STEP']],
            body: (data.resolution_steps || []).map((step, i) => [i + 1, step]),
            theme: 'striped',
            headStyles: { fillColor: [16, 185, 129] }
        });

        doc.save(`Incident_Report_${new Date().getTime()}.pdf`);
    };

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Intelligence Header */}
            <div className="glass-panel p-6 border-t-4 border-brand-primary rounded-2xl">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <i className="fas fa-microchip text-brand-primary"></i>
                        <h3 className="text-lg font-bold text-white uppercase tracking-tighter">AI Summary</h3>
                    </div>
                    <div className="flex items-center gap-3">
                        <button 
                            onClick={generatePDF}
                            className="text-xs font-bold text-slate-400 hover:text-white flex items-center gap-2 border border-white/10 px-3 py-1.5 rounded-lg bg-white/5 transition-all"
                        >
                            <i className="fas fa-file-pdf text-red-400"></i> EXPORT PDF
                        </button>
                        <span className={`px-3 py-1 rounded-lg border text-[10px] font-bold uppercase tracking-widest ${sourceColors[data.source] || 'bg-slate-500/10 border-slate-500/20 text-slate-400'}`}>
                            {data.source || 'Analysis'}
                        </span>
                    </div>
                </div>
                <p className="text-lg text-slate-300 font-medium leading-relaxed font-display italic">
                    "{data.summary}"
                </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Diagnostics */}
                <div className="space-y-6">
                    <div className="glass-panel p-6 border-l-4 border-red-500 rounded-2xl">
                        <h3 className="text-red-400 font-bold text-xs uppercase tracking-widest mb-4 flex items-center gap-2">
                            <i className="fas fa-search-location"></i> Confirmed Root Cause
                        </h3>
                        <p className="text-white text-base font-medium leading-relaxed">
                            {data.root_cause}
                        </p>
                    </div>

                    <div className="glass-panel p-6 border-l-4 border-amber-500 rounded-2xl">
                        <h3 className="text-amber-400 font-bold text-xs uppercase tracking-widest mb-4 flex items-center gap-2">
                             <i className="fas fa-fire-extinguisher"></i> Immediate Mitigation
                        </h3>
                        <div className="space-y-3">
                            {(data.immediate_actions || []).map((action, i) => (
                                <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-white/5 border border-white/5">
                                    <span className="mt-1 w-1.5 h-1.5 rounded-full bg-amber-500 shadow-lg shadow-amber-500/40"></span>
                                    <p className="text-sm text-slate-300 font-medium">{action.step}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Metrics & Confidence */}
                <div className="space-y-6">
                    <div className="glass-panel p-6 border-l-4 border-indigo-500 rounded-2xl h-full">
                        <h3 className="text-indigo-400 font-bold text-xs uppercase tracking-widest mb-6 flex items-center gap-2">
                             <i className="fas fa-chart-line"></i> Intelligence Metrics
                        </h3>
                        
                        <div className="space-y-8">
                            <div>
                                <div className="flex justify-between items-end mb-2">
                                    <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Confidence Score</span>
                                    <span className="text-2xl font-display font-bold text-white">{data.confidence}</span>
                                </div>
                                <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                                    <div 
                                        className="bg-brand-primary h-full rounded-full transition-all duration-1000" 
                                        style={{ width: data.confidence }}
                                    ></div>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 rounded-2xl bg-slate-800/50 border border-white/5">
                                    <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Severity</div>
                                    <div className={`text-xl font-bold ${data.severity?.includes('1') ? 'text-red-400' : 'text-amber-400'}`}>
                                        {data.severity}
                                    </div>
                                </div>
                                <div className="p-4 rounded-2xl bg-slate-800/50 border border-white/5">
                                    <div className="text-[10px] text-slate-500 uppercase font-bold mb-1">Complexity</div>
                                    <div className="text-xl font-bold text-white">
                                        {data.complexity?.toUpperCase()}
                                    </div>
                                </div>
                            </div>

                            <div className="p-4 rounded-2xl bg-brand-primary/10 border border-brand-primary/20 flex items-center justify-between">
                                <div className="text-sm font-medium text-slate-300">Suggested Responder</div>
                                <span className="text-xs font-bold text-brand-primary flex items-center gap-2">
                                    <i className="fas fa-user-tag"></i> {data.primary_owner || 'DEVOPS / SRE'}
                                </span>
                            </div>

                            <div className="p-4 rounded-2xl bg-brand-primary/5 border border-brand-primary/10 flex items-center justify-between">
                                <div className="text-sm font-medium text-slate-300">Learning Status</div>
                                {data.source === 'KEDB' ? (
                                    <span className="text-xs font-bold text-emerald-400 flex items-center gap-2">
                                        <i className="fas fa-check-circle"></i> VERIFIED IN KEDB
                                    </span>
                                ) : (
                                    <span className="text-xs font-bold text-blue-400 flex items-center gap-2">
                                        <i className="fas fa-plus-circle"></i> CANDIDATE FOR KEDB
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Resolution Path */}
            <div className="glass-panel p-6 border-l-4 border-emerald-500 rounded-2xl">
                 <h3 className="text-emerald-400 font-bold text-xs uppercase tracking-widest mb-4 flex items-center gap-2">
                    <i className="fas fa-clipboard-list"></i> Resolution Path (Step-by-Step)
                </h3>
                <div className="space-y-4">
                    {(data.resolution_steps || []).map((step, i) => (
                        <div key={i} className="flex items-center gap-4 group">
                            <div className="w-6 h-6 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px] font-bold">
                                {i + 1}
                            </div>
                            <p className="flex-1 text-slate-300 text-sm group-hover:text-white transition-colors">{step}</p>
                            <button className="opacity-0 group-hover:opacity-100 p-2 hover:bg-white/5 rounded-lg transition-all text-slate-500 hover:text-white">
                                <i className="fas fa-copy text-xs"></i>
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

const RightPanel = ({ data }) => (
    <div className="w-80 glass-panel h-screen flex flex-col p-4 z-10">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2">
            <i className="fas fa-project-diagram"></i> Intelligence Correlation
        </h3>
        
        {!data?.similar_incidents?.length ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center opacity-30 mt-20">
                <i className="fas fa-layer-group text-3xl mb-4"></i>
                <p className="text-xs font-medium">No historical<br/>matches identified</p>
            </div>
        ) : (
            <div className="space-y-4 overflow-y-auto pr-2">
                {data.similar_incidents.map((inc, i) => (
                    <div key={i} className="p-4 rounded-xl bg-slate-900 border border-white/5 hover:border-brand-primary/30 transition-all group cursor-pointer">
                        <div className="flex items-center justify-between mb-2">
                             <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${inc.source === 'KEDB' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-blue-500/10 text-blue-400'}`}>
                                {inc.source}
                             </span>
                             <i className="fas fa-chevron-right text-[10px] text-slate-700 group-hover:text-brand-primary transition-colors"></i>
                        </div>
                        <p className="text-xs font-bold text-white mb-2 line-clamp-2">{inc.issue}</p>
                        <p className="text-[10px] text-slate-500 line-clamp-3 leading-relaxed italic border-l border-white/5 pl-2">
                            "{inc.root_cause}"
                        </p>
                    </div>
                ))}
                
                <div className="p-4 rounded-xl bg-brand-primary/5 border border-brand-primary/10 border-dashed text-center">
                    <p className="text-[10px] text-brand-primary font-bold">Vector Memory: Full Integrity</p>
                </div>
            </div>
        )}

        <div className="mt-auto space-y-4 pt-4 border-t border-white/5">
             <div className="text-[10px] text-slate-600 uppercase font-bold tracking-tighter">Live Session Telemetry</div>
             <div className="flex items-center justify-between">
                 <span className="text-[10px] text-slate-400">Total Retrieved</span>
                 <span className="text-[10px] font-mono text-slate-300">{data?.similar_incidents?.length || 0}</span>
             </div>
             <div className="flex items-center justify-between">
                 <span className="text-[10px] text-slate-400">API Latency</span>
                 <span className="text-[10px] font-mono text-slate-300">124ms</span>
             </div>
        </div>
    </div>
);

const App = () => {
    const [incidentText, setIncidentText] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const [feedbackLoading, setFeedbackLoading] = useState(false);
    const [feedbackSuccess, setFeedbackSuccess] = useState(null);

    const fileInputRef = useRef(null);

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        // Visual feedback
        setLoading(true);

        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            setIncidentText(content);
            setLoading(false);
        };
        reader.onerror = () => {
             setError("Failed to read file.");
             setLoading(false);
        };
        reader.readAsText(file);
    };

    const handleAnalyze = async () => {
        if (!incidentText.trim()) return;
        
        setLoading(true);
        setError(null);
        setResult(null);
        setFeedbackSuccess(null);
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ incident: incidentText })
            });
            const data = await response.json();
            
            if (data.success) {
                setResult(data.data);
            } else {
                setError(data.error);
            }
        } catch (err) {
            setError('System error. Failed to reach intelligence engine.');
        } finally {
            setLoading(false);
        }
    };

    const submitFeedback = async () => {
        if (!result) return;
        setFeedbackLoading(true);
        try {
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    incident: incidentText,
                    ...result
                })
            });
            const data = await response.json();
            if (data.success) {
                setFeedbackSuccess('Intelligence stored in KEDB successfully.');
            }
        } catch (err) {
            setError('Failed to submit feedback.');
        } finally {
            setFeedbackLoading(false);
        }
    };

    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar />
            
            <main className="flex-1 flex flex-col bg-slate-950/20">
                <Navbar />
                
                <div className="flex-1 overflow-y-auto p-8 scroll-smooth">
                    <div className="max-w-4xl mx-auto space-y-8">
                        {/* Summary Header */}
                        <div>
                            <h2 className="text-3xl font-display font-bold text-white mb-2">Diagnostic Console</h2>
                            <p className="text-slate-500 text-sm">Analyze logs and symptoms using multi-source intelligence correlation.</p>
                        </div>

                        {/* Input Area */}
                        <div className="glass-panel p-6 rounded-3xl relative group">
                            <div className="absolute top-4 right-6 pointer-events-none text-[10px] text-slate-700 font-mono tracking-widest uppercase group-focus-within:text-brand-primary transition-colors">
                                Input Buffer
                            </div>
                            <textarea
                                className="w-full h-40 bg-transparent border-none text-slate-200 placeholder-slate-700 focus:ring-0 resize-none font-mono text-sm leading-relaxed"
                                placeholder="Paste incident logs, stack traces, or observed errors..."
                                value={incidentText}
                                onChange={(e) => setIncidentText(e.target.value)}
                                disabled={loading}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleAnalyze();
                                }}
                            />
                            <input 
                                type="file" 
                                ref={fileInputRef} 
                                className="hidden" 
                                onChange={handleFileUpload}
                                accept=".txt,.log,.json,.csv"
                            />
                            <div className="flex items-center justify-between mt-4">
                                <div className="flex gap-2">
                                     <button 
                                        className="px-3 py-1.5 rounded-lg bg-slate-800 text-[10px] font-bold text-slate-400 hover:text-white transition-colors border border-white/5"
                                        onClick={() => fileInputRef.current.click()}
                                    >
                                        <i className="fas fa-file-upload mr-2"></i> ATTACH LOGS
                                    </button>
                                     <button className="px-3 py-1.5 rounded-lg bg-slate-800 text-[10px] font-bold text-slate-400 hover:text-white transition-colors border border-white/5"
                                        onClick={() => setIncidentText("ERROR [server-8] Connection pool exhausted. 154 threads waiting for lock. \n[LOG] service=orders instance=o-123 timestamp=1623456789\n[LOG] level=fatal message=\"OOM Killer invoked\"")}>
                                        <i className="fas fa-magic mr-2"></i> LOAD EXAMPLE
                                    </button>
                                </div>
                                <button 
                                    className="btn-primary flex items-center gap-2"
                                    onClick={handleAnalyze}
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <>
                                            <i className="fas fa-circle-notch animate-spin"></i>
                                            Analyzing...
                                        </>
                                    ) : (
                                        <>
                                            Analyze Incident <span className="text-[10px] opacity-60 bg-white/10 px-1.5 py-0.5 rounded ml-1 font-mono">⌘↵</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-3 animate-shake">
                                <i className="fas fa-exclamation-triangle"></i>
                                {error}
                            </div>
                        )}

                        {feedbackSuccess && (
                            <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm flex items-center gap-3 animate-fade-in text-center justify-center">
                                <i className="fas fa-check-circle"></i>
                                {feedbackSuccess}
                            </div>
                        )}

                        <ResultsPanel data={result} loading={loading} />

                        {result && !feedbackSuccess && (
                            <div className="flex justify-center pt-8 border-t border-white/5">
                                <button 
                                    className="px-8 py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition-all shadow-xl shadow-emerald-600/20 hover:-translate-y-1 active:scale-95 flex items-center gap-3"
                                    onClick={submitFeedback}
                                    disabled={feedbackLoading}
                                >
                                    {feedbackLoading ? (
                                         <i className="fas fa-circle-notch animate-spin"></i>
                                    ) : (
                                        <i className="fas fa-database"></i>
                                    )}
                                    Confirm Resolution & Store in KEDB
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </main>

            <RightPanel data={result} />
        </div>
    );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
