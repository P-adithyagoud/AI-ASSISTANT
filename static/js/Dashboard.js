/**
 * SRE COMMANDER | AI INCIDENT INTELLIGENCE
 * Production-grade SaaS Dashboard Frontend
 * Powered by React, Tailwind CSS, and Lucide Icons.
 */

const { useState, useEffect, useRef } = React;

// --- CONFIGURATION & CONSTANTS ---

const SOURCE_THEMES = {
    'KEDB': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    'VECTOR DB': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    'LLM_FALLBACK': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    'fallback': 'bg-purple-500/10 text-purple-400 border-purple-500/20'
};

const LOG_TELEMETRY = (msg) => console.log(`%c[SRE-TELEMETRY] %c${msg}`, 'color: #3b82f6; font-weight: bold;', 'color: #94a3b8;');

// --- SUB-COMPONENTS ---

/**
 * Sidebar component for primary navigation.
 */
const Sidebar = () => (
    <aside className="w-64 glass-panel h-screen flex flex-col p-4 z-10">
        <div className="flex items-center gap-3 px-2 mb-10">
            <div className="w-8 h-8 bg-brand-primary rounded-lg flex items-center justify-center shadow-lg shadow-brand-primary/20">
                <i className="fas fa-microchip text-white text-sm"></i>
            </div>
            <h1 className="font-display font-bold text-lg tracking-tight">SRE Commander</h1>
        </div>
        
        <nav className="flex-1 space-y-1">
            <NavItem icon="fas fa-columns" label="Dashboard" active />
            <NavItem icon="fas fa-list-ul" label="Incidents" />
            <NavItem icon="fas fa-database" label="KEDB" />
            <NavItem icon="fas fa-chart-pie" label="Analytics" />
        </nav>

        <div className="mt-auto border-t border-white/5 pt-4">
            <NavItem icon="fas fa-cog" label="Settings" />
            <div className="mt-4 px-2 py-3 rounded-xl bg-slate-950/50 border border-white/5 shadow-inner">
                <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-2">System Health</div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span className="text-xs text-slate-300">Clusters Operational</span>
                </div>
            </div>
        </div>
    </aside>
);

const NavItem = ({ icon, label, active = false }) => (
    <div className={`sidebar-link ${active ? 'active' : ''}`}>
        <i className={icon}></i>
        <span>{label}</span>
    </div>
);

/**
 * Top Navbar component with environment tags.
 */
const Navbar = () => (
    <header className="h-16 border-b border-white/5 px-8 flex items-center justify-between bg-slate-950/20 backdrop-blur-sm">
        <div className="flex items-center gap-4">
            <div className="text-xs font-bold text-slate-500 uppercase tracking-widest">Environment:</div>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                PRODUCTION
            </div>
        </div>
        <div className="flex items-center gap-6">
            <div className="text-right hidden sm:block">
                <div className="text-sm font-semibold text-white">SRE Lead</div>
                <div className="text-[10px] text-slate-500">Cloud Operations Unit</div>
            </div>
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-brand-primary to-brand-secondary p-[1px] shadow-lg shadow-brand-primary/10">
                <div className="w-full h-full rounded-full bg-slate-900 flex items-center justify-center border border-white/10 overflow-hidden">
                    <i className="fas fa-user-shield text-brand-primary text-lg"></i>
                </div>
            </div>
        </div>
    </header>
);

/**
 * Skeleton Card for loading states.
 */
const SkeletonCard = () => (
    <div className="glass-panel p-6 space-y-4 rounded-2xl">
        <div className="skeleton h-6 w-1/3"></div>
        <div className="skeleton h-24 w-full"></div>
        <div className="flex gap-4">
            <div className="skeleton h-8 w-1/4"></div>
            <div className="skeleton h-8 w-1/4"></div>
        </div>
    </div>
);

// --- MAIN FEATURE COMPONENTS ---

/**
 * ResultsPanel: Handles conditional rendering of the AI Analysis results.
 */
const ResultsPanel = ({ data, loading }) => {
    if (loading) return (
        <div className="space-y-6 animate-pulse mt-8">
            <SkeletonCard />
            <div className="grid grid-cols-2 gap-6">
                <SkeletonCard />
                <SkeletonCard />
            </div>
        </div>
    );

    if (!data) return <EmptyState />;

    const handleExportPDF = () => {
        LOG_TELEMETRY("Generating incident report PDF...");
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        // Brand Header (Export Styling)
        doc.setFillColor(15, 23, 42); 
        doc.rect(0, 0, 210, 40, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(22);
        doc.setFont("helvetica", "bold");
        doc.text("SRE COMMANDER REPORT", 20, 20);
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");
        doc.text(`DATE: ${new Date().toLocaleString()}`, 140, 30);

        // Core Data Generation
        doc.autoTable({
            startY: 50,
            head: [['ANALYSIS CATEGORY', 'DETAILS']],
            body: [
                ['INCIDENT SUMMARY', data.summary],
                ['ROOT CAUSE', data.root_cause],
                ['SEVERITY', data.severity],
                ['SUGGESTED OWNER', data.primary_owner]
            ],
            theme: 'grid',
            headStyles: { fillColor: [59, 130, 246] }
        });

        doc.autoTable({
            startY: doc.lastAutoTable.finalY + 10,
            head: [['#', 'RESOLUTION STEP']],
            body: (data.resolution_steps || []).map((step, i) => [i + 1, step]),
            theme: 'striped',
            headStyles: { fillColor: [16, 185, 129] }
        });

        doc.save(`Incident_Report_${Date.now()}.pdf`);
    };

    return (
        <div className="space-y-6 animate-fade-in mt-8">
            {/* Analysis Header */}
            <AnalysisCard data={data} onExport={handleExportPDF} theme={SOURCE_THEMES[data.source]} />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Diagnostics */}
                <div className="space-y-6">
                    <InfoCard 
                        title="Confirmed Root Cause" 
                        icon="fas fa-search-location"
                        color="red"
                        content={data.root_cause} 
                    />
                    <StepCard 
                        title="Immediate Mitigation" 
                        icon="fas fa-fire-extinguisher"
                        color="amber"
                        steps={data.immediate_actions} 
                    />
                </div>

                {/* Intelligence Metrics */}
                <MetricsCard data={data} />
            </div>

            {/* Resolution Board */}
            <ResolutionCard steps={data.resolution_steps} />
        </div>
    );
};

const EmptyState = () => (
    <div className="h-full flex flex-col items-center justify-center text-center p-12 opacity-50 mt-20">
        <div className="w-24 h-24 mb-6 rounded-3xl bg-slate-900 border border-white/5 flex items-center justify-center text-4xl text-slate-700 shadow-2xl">
            <i className="fas fa-terminal"></i>
        </div>
        <h3 className="text-xl font-display font-medium text-slate-400 mb-2">Diagnostic Data Required</h3>
        <p className="max-w-xs text-sm text-slate-500 leading-relaxed italic">
            Analyze logs or symptoms to trigger multi-source intelligence correlation.
        </p>
    </div>
);

const AnalysisCard = ({ data, onExport, theme }) => (
    <div className="glass-panel p-6 border-t-4 border-brand-primary rounded-2xl shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-brand-primary/5 blur-3xl -z-10"></div>
        <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
                <i className="fas fa-microchip text-brand-primary"></i>
                <h3 className="text-lg font-bold text-white uppercase tracking-tighter">AI Summary</h3>
            </div>
            <div className="flex items-center gap-3">
                <button 
                    onClick={onExport}
                    className="text-xs font-bold text-slate-400 hover:text-white flex items-center gap-2 border border-white/10 px-3 py-1.5 rounded-lg bg-white/5 transition-all hover:bg-white/10 active:scale-95"
                >
                    <i className="fas fa-file-pdf text-red-500"></i> EXPORT REPORT
                </button>
                <div className={`px-3 py-1 rounded-lg border text-[10px] font-bold uppercase tracking-widest ${theme || 'bg-slate-500/10 border-slate-500/20 text-slate-400'}`}>
                    {data.source || 'Standard'}
                </div>
            </div>
        </div>
        <p className="text-lg text-slate-200 font-medium leading-relaxed font-display italic">
            "{data.summary}"
        </p>
    </div>
);

const InfoCard = ({ title, icon, color, content }) => (
    <div className={`glass-panel p-6 border-l-4 border-${color}-500 rounded-2xl shadow-lg`}>
        <h3 className={`text-${color}-400 font-bold text-xs uppercase tracking-widest mb-4 flex items-center gap-2`}>
            <i className={icon}></i> {title}
        </h3>
        <p className="text-white text-base font-medium leading-relaxed">
            {content}
        </p>
    </div>
);

const StepCard = ({ title, icon, color, steps }) => (
    <div className={`glass-panel p-6 border-l-4 border-${color}-500 rounded-2xl shadow-lg`}>
        <h3 className={`text-${color}-400 font-bold text-xs uppercase tracking-widest mb-4 flex items-center gap-2`}>
             <i className={icon}></i> {title}
        </h3>
        <div className="space-y-3">
            {(steps || []).map((action, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                    <span className={`mt-1.5 w-1.5 h-1.5 rounded-full bg-${color}-500 shadow-xl shadow-${color}-500/50`}></span>
                    <p className="text-sm text-slate-300 font-medium leading-snug">{action.step}</p>
                </div>
            ))}
        </div>
    </div>
);

const MetricsCard = ({ data }) => {
    const confidenceVal = parseInt(data.confidence) || 0;
    
    return (
        <div className="glass-panel p-6 border-l-4 border-indigo-500 rounded-2xl h-full shadow-lg">
            <h3 className="text-indigo-400 font-bold text-xs uppercase tracking-widest mb-6 flex items-center gap-2">
                 <i className="fas fa-chart-line"></i> Intelligence Metrics
            </h3>
            
            <div className="space-y-8">
                <div>
                    <div className="flex justify-between items-end mb-2">
                        <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Confidence Score</span>
                        <span className="text-2xl font-display font-bold text-white">{data.confidence}</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden shadow-inner font-mono">
                        <div 
                            className="bg-brand-primary h-full rounded-full transition-all duration-1000 shadow-[0_0_8px_rgba(59,130,246,0.5)]" 
                            style={{ width: `${Math.min(confidenceVal, 100)}%` }}
                        ></div>
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <MetricBadge label="Severity" value={data.severity} highlight={data.severity?.includes('1')} />
                    <MetricBadge label="Complexity" value={data.complexity?.toUpperCase()} />
                </div>

                <div className="p-4 rounded-2xl bg-brand-primary/10 border border-brand-primary/20 flex items-center justify-between shadow-sm">
                    <div className="text-sm font-medium text-slate-300">Suggested Responder</div>
                    <span className="text-xs font-bold text-brand-primary flex items-center gap-2">
                        <i className="fas fa-user-tag text-[10px]"></i> {data.primary_owner || 'DEVOPS / SRE'}
                    </span>
                </div>

                <div className="p-4 rounded-2xl bg-brand-primary/5 border border-brand-primary/10 flex items-center justify-between opacity-80">
                    <div className="text-sm font-medium text-slate-400">Knowledge Type</div>
                    {data.source === 'KEDB' ? (
                        <span className="text-xs font-bold text-emerald-400/80 flex items-center gap-2 uppercase tracking-tight">
                            <i className="fas fa-check-circle"></i> Local Verified
                        </span>
                    ) : (
                        <span className="text-xs font-bold text-blue-400/80 flex items-center gap-2 uppercase tracking-tight">
                            <i className="fas fa-brain"></i> Neural Logic
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
};

const MetricBadge = ({ label, value, highlight = false }) => (
    <div className="p-4 rounded-2xl bg-slate-800/50 border border-white/5 group hover:border-white/10 transition-colors">
        <div className="text-[10px] text-slate-500 uppercase font-bold mb-1 tracking-wider">{label}</div>
        <div className={`text-xl font-bold ${highlight ? 'text-red-400 drop-shadow-[0_0_8px_rgba(248,113,113,0.3)]' : 'text-white'}`}>
            {value}
        </div>
    </div>
);

const ResolutionCard = ({ steps }) => (
    <div className="glass-panel p-6 border-l-4 border-emerald-500 rounded-2xl shadow-lg mt-10">
         <h3 className="text-emerald-400 font-bold text-xs uppercase tracking-widest mb-6 flex items-center gap-2">
            <i className="fas fa-clipboard-list"></i> Resolution Path (Step-by-Step)
        </h3>
        <div className="space-y-4">
            {(steps || []).map((step, i) => (
                <div key={i} className="flex items-center gap-4 group">
                    <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center text-[11px] font-bold shadow-sm">
                        {i + 1}
                    </div>
                    <p className="flex-1 text-slate-300 text-sm group-hover:text-white transition-colors py-1">{step}</p>
                    <button 
                        className="opacity-0 group-hover:opacity-100 p-2.5 hover:bg-white/5 rounded-xl transition-all text-slate-500 hover:text-white active:scale-90"
                        onClick={() => {navigator.clipboard.writeText(step); LOG_TELEMETRY("Copied resolution step.");}}
                        title="Copy Step"
                    >
                        <i className="fas fa-copy text-xs"></i>
                    </button>
                </div>
            ))}
        </div>
    </div>
);

/**
 * Historical Correlation Side-panel.
 */
const RightPanel = ({ data }) => (
    <div className="w-80 glass-panel h-screen flex flex-col p-4 z-10 hidden xl:flex">
        <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-6 flex items-center gap-2">
            <i className="fas fa-project-diagram"></i> Intelligence Correlation
        </h3>
        
        {!data?.similar_incidents?.length ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center opacity-20 mt-20">
                <i className="fas fa-layer-group text-4xl mb-4"></i>
                <p className="text-xs font-semibold uppercase tracking-wider">Passive Mode<br/>Monitoring Memory</p>
            </div>
        ) : (
            <div className="space-y-4 overflow-y-auto pr-2 custom-scrollbar">
                {data.similar_incidents.map((inc, i) => (
                    <div key={i} className="p-4 rounded-xl bg-slate-900/80 border border-white/5 hover:border-brand-primary/40 transition-all group cursor-pointer shadow-md hover:shadow-brand-primary/10">
                        <div className="flex items-center justify-between mb-2">
                             <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded shadow-sm ${inc.source === 'KEDB' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-blue-500/10 text-blue-400'}`}>
                                {inc.source}
                             </span>
                             <i className="fas fa-external-link-alt text-[9px] text-slate-700 group-hover:text-brand-primary transition-colors"></i>
                        </div>
                        <p className="text-xs font-bold text-white mb-2 line-clamp-2 leading-tight">{inc.issue}</p>
                        <p className="text-[10px] text-slate-500 line-clamp-4 leading-relaxed italic border-l-2 border-slate-800 pl-3">
                            "{inc.root_cause}"
                        </p>
                    </div>
                ))}
            </div>
        )}

        <div className="mt-auto space-y-4 pt-6 border-t border-white/5">
             <div className="text-[10px] text-slate-600 uppercase font-black tracking-widest">Telemetry Stream</div>
             <TelemetryRow label="Resolved Matches" value={data?.similar_incidents?.length || 0} />
             <TelemetryRow label="Session Depth" value={(data?.similar_incidents?.length || 0) * 1.5 + "kb"} />
             <TelemetryRow label="Analytic Latency" value={data ? "142ms" : "0ms"} />
        </div>
    </div>
);

const TelemetryRow = ({ label, value }) => (
    <div className="flex items-center justify-between border-b border-white/5 pb-2 last:border-0">
        <span className="text-[10px] text-slate-500 font-medium">{label}</span>
        <span className="text-[10px] font-mono text-brand-primary font-bold">{value}</span>
    </div>
);

// --- MAIN APPLICATION CONTEXT ---

const App = () => {
    // --- STATE ---
    const [incidentText, setIncidentText] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [feedbackLoading, setFeedbackLoading] = useState(false);
    const [feedbackSuccess, setFeedbackSuccess] = useState(null);

    const fileInputRef = useRef(null);

    // --- HANDLERS ---

    /**
     * Reads a log file from the local disk and populates the text buffer.
     */
    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        LOG_TELEMETRY(`Ingesting file: ${file.name}`);
        setLoading(true);

        const reader = new FileReader();
        reader.onload = (e) => {
            setIncidentText(e.target.result);
            setLoading(false);
            LOG_TELEMETRY("File ingest successful.");
        };
        reader.onerror = () => {
             setError("Failed to read binary stream.");
             setLoading(false);
        };
        reader.readAsText(file);
    };

    /**
     * Submits the diagnostic request to the Flask backend.
     */
    const handleAnalyze = async () => {
        if (!incidentText.trim()) return;
        
        LOG_TELEMETRY("Initiating analysis chain...");
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
                LOG_TELEMETRY(`Correlation complete. Source: ${data.data.source}`);
                setResult(data.data);
            } else {
                setError(data.error || "Analysis failed.");
            }
        } catch (err) {
            setError('Upstream system timeout. Connection lost.');
        } finally {
            setLoading(false);
        }
    };

    /**
     * Commits the current analysis to the KEDB.
     */
    const submitFeedback = async () => {
        if (!result) return;
        setFeedbackLoading(true);
        LOG_TELEMETRY("Committing resolution to KEDB clusters...");
        try {
            const response = await fetch('/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ incident: incidentText, ...result })
            });
            const data = await response.json();
            if (data.success) {
                setFeedbackSuccess('Intelligence synchronized with global KEDB.');
                LOG_TELEMETRY("Deduplication and ingestion phase complete.");
            }
        } catch (err) {
            setError('Knowledge ingestion failed.');
        } finally {
            setFeedbackLoading(false);
        }
    };

    // --- RENDER ---
    return (
        <div className="flex h-screen overflow-hidden font-sans">
            <Sidebar />
            
            <main className="flex-1 flex flex-col bg-slate-950/40 relative">
                {/* Visual Background Elements */}
                <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-brand-primary/5 rounded-full blur-[120px] pointer-events-none"></div>
                <div className="absolute bottom-0 left-1/4 w-[400px] h-[400px] bg-brand-secondary/5 rounded-full blur-[100px] pointer-events-none"></div>

                <Navbar />
                
                <div className="flex-1 overflow-y-auto p-6 lg:p-10 scroll-smooth custom-scrollbar">
                    <div className="max-w-5xl mx-auto space-y-10">
                        
                        {/* Title Section */}
                        <div className="flex flex-col gap-1">
                            <h2 className="text-4xl font-display font-bold text-white tracking-tight">Diagnostic Console</h2>
                            <p className="text-slate-500 text-sm font-medium">Neural engine ready for log stream analysis and historical correlation.</p>
                        </div>

                        {/* Input & Control Card */}
                        <div className="glass-panel p-8 rounded-[2rem] relative group border-white/5 hover:border-white/10 transition-all shadow-2xl">
                            <div className="absolute top-5 right-8 pointer-events-none text-[10px] text-slate-700 font-bold tracking-widest uppercase group-focus-within:text-brand-primary transition-all">
                                [ BUFFER 01 ]
                            </div>
                            
                            <textarea
                                className="w-full h-44 bg-transparent border-none text-slate-100 placeholder-slate-800 focus:ring-0 resize-none font-mono text-sm leading-relaxed scrollbar-hide"
                                placeholder="Paste incident logs, traces, or observed error patterns here..."
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

                            <div className="flex flex-wrap items-center justify-between mt-6 gap-4">
                                <div className="flex gap-3">
                                     <button 
                                        className="h-10 px-4 rounded-xl bg-slate-900 text-[10px] font-black text-slate-500 hover:text-white transition-all border border-white/5 hover:bg-slate-800 flex items-center gap-2 group/btn"
                                        onClick={() => fileInputRef.current.click()}
                                    >
                                        <i className="fas fa-file-upload text-brand-primary transition-transform group-hover/btn:-translate-y-0.5"></i> 
                                        ATTACH DATA STREAM
                                    </button>
                                     <button 
                                        className="h-10 px-4 rounded-xl bg-slate-900 text-[10px] font-black text-slate-500 hover:text-white transition-all border border-white/5 hover:bg-slate-800 flex items-center gap-2"
                                        onClick={() => setIncidentText("CRITICAL ERROR: Connection pool [DB-PRD-01] exhausted. \nWAIT_TIME: 4500ms | THREADS: 120/120\n[PROXY] service=api node=edge-4 timestamp=1623456789\nLEVEL=FATAL")}>
                                        <i className="fas fa-magic text-brand-secondary"></i> LOAD SIMULATION
                                    </button>
                                </div>

                                <button 
                                    className="btn-primary h-12 flex items-center gap-3 shadow-brand-primary/20 text-sm"
                                    onClick={handleAnalyze}
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <i className="fas fa-circle-notch animate-spin text-base"></i>
                                    ) : (
                                        <>
                                            <i className="fas fa-bolt"></i> ANALYZE INCIDENT 
                                            <span className="text-[10px] opacity-40 font-mono tracking-tighter">⌘↵</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* Error & Success States */}
                        <NotificationArea error={error} success={feedbackSuccess} />

                        {/* Results Hub */}
                        <ResultsPanel data={result} loading={loading} />

                        {/* Finalization Action */}
                        <ActionArea 
                            visible={!!result && !feedbackSuccess}
                            onConfirm={submitFeedback}
                            loading={feedbackLoading}
                        />

                    </div>
                    <div className="h-20"></div> {/* Bottom spacing */}
                </div>
            </main>

            <RightPanel data={result} />
        </div>
    );
};

// --- HELPER WRAPPERS ---

const NotificationArea = ({ error, success }) => (
    <div className="space-y-4">
        {error && (
            <div className="p-5 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm font-medium flex items-center gap-4 shadow-lg animate-shake">
                <i className="fas fa-exclamation-triangle text-base"></i>
                <div className="flex-1">{error}</div>
            </div>
        )}
        {success && (
            <div className="p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-bold flex items-center gap-4 shadow-lg animate-fade-in text-center justify-center border-dashed">
                <i className="fas fa-check-circle text-lg"></i>
                {success}
            </div>
        )}
    </div>
);

const ActionArea = ({ visible, onConfirm, loading }) => {
    if (!visible) return null;
    return (
        <div className="flex justify-center pt-8 border-t border-white/5 animate-fade-up">
            <button 
                className="px-10 py-5 rounded-3xl bg-emerald-600 hover:bg-emerald-500 text-white font-black text-xs uppercase tracking-widest transition-all shadow-2xl shadow-emerald-600/30 hover:-translate-y-1 active:scale-95 flex items-center gap-3 border border-emerald-400/20"
                onClick={onConfirm}
                disabled={loading}
            >
                {loading ? (
                    <i className="fas fa-sync animate-spin"></i>
                ) : (
                    <i className="fas fa-database text-sm"></i>
                )}
                Confirm Knowledge & Sync to KEDB
            </button>
        </div>
    );
};

// --- INITIALIZATION ---

const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);
root.render(<App />);
