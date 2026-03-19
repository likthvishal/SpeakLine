import { Mic, Play, ArrowRight, Sparkles } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-16 overflow-hidden">
      {/* Grid Pattern */}
      <div
        className="absolute inset-0 opacity-[0.08]"
        style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, rgb(156 163 175) 1px, transparent 0)`,
          backgroundSize: '40px 40px',
        }}
      />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-8 animate-fade-in">
          <Sparkles className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-500">Powered by OpenAI Whisper</span>
        </div>

        {/* Main Heading */}
        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 animate-slide-up">
          Turn Your Voice Into
          <br />
          <span className="gradient-text">Code Comments</span>
        </h1>

        {/* Subheading */}
        <p className="text-xl text-gray-500 max-w-2xl mx-auto mb-10 animate-slide-up" style={{ animationDelay: '0.1s' }}>
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
            <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-200 bg-gray-50">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-yellow-400" />
                <div className="w-3 h-3 rounded-full bg-green-400" />
              </div>
              <span className="text-gray-400 text-sm ml-2">terminal</span>
            </div>
            <div className="p-4 font-mono text-sm leading-relaxed">
              <p className="text-gray-400"># Record and insert comment at line 42</p>
              <p>
                <span className="text-green-700">$</span>{' '}
                <span className="text-blue-600">speakline</span>{' '}
                <span className="text-orange-600">record</span>{' '}
                <span className="text-gray-700">myfile.py 42</span>
              </p>
              <p className="text-gray-400 mt-4"># Preview before writing:</p>
              <p>
                <span className="text-green-700">$</span>{' '}
                <span className="text-blue-600">speakline</span>{' '}
                <span className="text-orange-600">record</span>{' '}
                <span className="text-gray-700">myfile.py 42 --preview</span>
              </p>
              <p className="text-gray-900 mt-2 font-medium">PREVIEW MODE (file not modified)</p>
              <p className="text-green-700">Ready to commit!</p>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <a href="#features" className="text-gray-400 hover:text-gray-900 transition-colors">
            <ArrowRight className="w-6 h-6 rotate-90" />
          </a>
        </div>
      </div>
    </section>
  );
}
