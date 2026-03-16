import { useState } from 'react';
import { Mic, Square, Check, Volume2 } from 'lucide-react';

export default function Demo() {
  const [isRecording, setIsRecording] = useState(false);
  const [showResult, setShowResult] = useState(false);

  const handleRecord = () => {
    setIsRecording(true);
    setShowResult(false);
    setTimeout(() => {
      setIsRecording(false);
      setShowResult(true);
    }, 3000);
  };

  const codeExample = `def calculate_total(items):
    # Calculate the sum of all item prices with tax applied
    total = 0
    for item in items:
        total += item.price * 1.08
    return total`;

  const codeWithComment = `def calculate_total(items):
    # This function calculates the total price including 8% tax
    # Calculate the sum of all item prices with tax applied
    total = 0
    for item in items:
        total += item.price * 1.08
    return total`;

  return (
    <section id="demo" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            See It In
            <span className="gradient-text"> Action</span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            Watch how VoiceComment transforms your spoken thoughts into clean, properly formatted code comments.
          </p>
        </div>

        {/* Demo Container */}
        <div className="max-w-4xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Recording Panel */}
            <div className="glass rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Volume2 className="w-5 h-5 text-sky-400" />
                Voice Input
              </h3>

              <div className="flex flex-col items-center py-8">
                <button
                  onClick={handleRecord}
                  disabled={isRecording}
                  className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 ${
                    isRecording
                      ? 'bg-red-500 animate-pulse'
                      : 'bg-gradient-to-br from-sky-500 to-violet-500 hover:scale-110'
                  }`}
                >
                  {isRecording ? (
                    <Square className="w-8 h-8 text-white" />
                  ) : (
                    <Mic className="w-10 h-10 text-white" />
                  )}
                </button>

                <p className="mt-4 text-slate-400 text-sm">
                  {isRecording ? 'Recording...' : 'Click to simulate recording'}
                </p>

                {/* Waveform Animation */}
                {isRecording && (
                  <div className="flex items-center gap-1 mt-6">
                    {[...Array(12)].map((_, i) => (
                      <div
                        key={i}
                        className="w-1 bg-sky-400 rounded-full animate-pulse"
                        style={{
                          height: `${Math.random() * 32 + 8}px`,
                          animationDelay: `${i * 0.1}s`,
                        }}
                      />
                    ))}
                  </div>
                )}

                {showResult && (
                  <div className="mt-6 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30 w-full">
                    <div className="flex items-center gap-2 text-emerald-400 mb-2">
                      <Check className="w-5 h-5" />
                      <span className="font-medium">Transcribed!</span>
                    </div>
                    <p className="text-slate-300 italic">
                      "This function calculates the total price including 8% tax"
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Code Panel */}
            <div className="glass rounded-2xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <span className="text-2xl">🐍</span>
                Code Output
              </h3>

              <div className="code-block">
                <div className="flex items-center gap-2 px-4 py-2 border-b border-slate-800 bg-slate-900/80">
                  <span className="text-slate-500 text-xs">calculate.py</span>
                </div>
                <pre className="p-4 text-sm overflow-x-auto">
                  <code>
                    {(showResult ? codeWithComment : codeExample).split('\n').map((line, i) => (
                      <div key={i} className="flex">
                        <span className="text-slate-600 w-6 text-right mr-4 select-none">{i + 1}</span>
                        <span className={line.includes('#') && showResult && i === 1 ? 'text-emerald-400' : ''}>
                          {line.startsWith('def') ? (
                            <>
                              <span className="token-keyword">def</span>
                              <span className="text-slate-300">{line.slice(3)}</span>
                            </>
                          ) : line.includes('#') ? (
                            <span className="token-comment">{line}</span>
                          ) : line.includes('for') ? (
                            <>
                              <span className="text-slate-300">{line.split('for')[0]}</span>
                              <span className="token-keyword">for</span>
                              <span className="text-slate-300">{line.split('for')[1]}</span>
                            </>
                          ) : line.includes('return') ? (
                            <>
                              <span className="text-slate-300">{line.split('return')[0]}</span>
                              <span className="token-keyword">return</span>
                              <span className="text-slate-300">{line.split('return')[1]}</span>
                            </>
                          ) : (
                            <span className="text-slate-300">{line}</span>
                          )}
                        </span>
                      </div>
                    ))}
                  </code>
                </pre>
              </div>

              {showResult && (
                <div className="mt-4 flex items-center gap-2 text-sm text-slate-400">
                  <Check className="w-4 h-4 text-emerald-400" />
                  Comment inserted at line 2 with proper indentation
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
