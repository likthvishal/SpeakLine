import { Mic, Brain, Code2, Puzzle, Terminal, Zap } from 'lucide-react';

const features = [
  {
    icon: Mic,
    title: 'Voice Recording',
    description: 'Local microphone input with intelligent silence detection. No cloud recording required.',
    color: 'from-sky-500 to-cyan-500',
  },
  {
    icon: Brain,
    title: 'AI Transcription',
    description: 'Powered by OpenAI Whisper. Run locally or use the API - your choice.',
    color: 'from-violet-500 to-purple-500',
  },
  {
    icon: Code2,
    title: 'Smart Insertion',
    description: 'Language-aware parsing with proper indentation. Comments that fit your code style.',
    color: 'from-emerald-500 to-teal-500',
  },
  {
    icon: Puzzle,
    title: 'Pluggable Backends',
    description: 'Swap recorders, transcribers, and parsers. Build your own integrations.',
    color: 'from-amber-500 to-orange-500',
  },
  {
    icon: Terminal,
    title: 'CLI & Python API',
    description: 'Use from terminal or import in your scripts. Jupyter notebook support included.',
    color: 'from-pink-500 to-rose-500',
  },
  {
    icon: Zap,
    title: 'Production Ready',
    description: 'Full type hints, comprehensive error handling, and extensive logging.',
    color: 'from-blue-500 to-indigo-500',
  },
];

export default function Features() {
  return (
    <section id="features" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            Everything You Need for
            <span className="gradient-text"> Voice-to-Code</span>
          </h2>
          <p className="text-slate-400 text-lg max-w-2xl mx-auto">
            A complete toolkit for turning your voice into well-formatted code comments,
            designed for developers who think faster than they type.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="feature-card group"
            >
              <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${feature.color} mb-4 group-hover:scale-110 transition-transform`}>
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
              <p className="text-slate-400">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
