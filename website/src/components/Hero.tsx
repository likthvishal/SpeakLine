import { Mic, Play, ArrowRight, Sparkles } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-16 overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-sky-500/20 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-violet-500/20 rounded-full blur-3xl animate-pulse-slow delay-1000" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-fuchsia-500/10 rounded-full blur-3xl" />
      </div>

      {/* Grid Pattern */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, rgb(148 163 184 / 0.3) 1px, transparent 0)`,
          backgroundSize: '40px 40px',
        }}
      />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8 animate-fade-in">
          <Sparkles className="w-4 h-4 text-amber-400" />
          <span className="text-sm text-slate-300">Powered by OpenAI Whisper</span>
        </div>

        {/* Main Heading */}
        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 animate-slide-up">
          Turn Your Voice Into
          <br />
          <span className="gradient-text">Code Comments</span>
        </h1>

        {/* Subheading */}
        <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          Record your thoughts, get perfectly formatted comments. Works with Python,
          JavaScript, TypeScript, Go, Rust, and 10+ languages.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16 animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <a href="#installation" className="btn-primary flex items-center gap-2 text-lg">
            <Mic className="w-5 h-5" />
            Get Started Free
          </a>
          <a href="#demo" className="btn-secondary flex items-center gap-2 text-lg">
            <Play className="w-5 h-5" />
            Watch Demo
          </a>
        </div>

        {/* Code Preview */}
        <div className="max-w-3xl mx-auto animate-slide-up" style={{ animationDelay: '0.3s' }}>
          <div className="code-block text-left">
            <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800 bg-slate-900/80">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-green-500/80" />
              </div>
              <span className="text-slate-500 text-sm ml-2">terminal</span>
            </div>
            <div className="p-4 font-mono text-sm leading-relaxed">
              <p className="text-slate-500"># Record and insert comment at line 42</p>
              <p>
                <span className="text-emerald-400">$</span>{' '}
                <span className="text-sky-400">speakline</span>{' '}
                <span className="text-amber-400">record</span>{' '}
                <span className="text-slate-300">myfile.py 42</span>
              </p>
              <p className="text-slate-500 mt-4"># Preview before writing:</p>
              <p>
                <span className="text-emerald-400">$</span>{' '}
                <span className="text-sky-400">speakline</span>{' '}
                <span className="text-amber-400">record</span>{' '}
                <span className="text-slate-300">myfile.py 42 --preview</span>
              </p>
              <p className="text-violet-400 mt-2">✓ PREVIEW MODE (file not modified)</p>
              <p className="text-emerald-400">Ready to commit!</p>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <a href="#features" className="text-slate-500 hover:text-white transition-colors">
            <ArrowRight className="w-6 h-6 rotate-90" />
          </a>
        </div>
      </div>
    </section>
  );
}
