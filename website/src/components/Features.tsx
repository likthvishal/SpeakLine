import { Mic, Brain, Code2, Puzzle, Terminal, Zap } from 'lucide-react';

const features = [
  {
    icon: Mic,
    title: 'Voice Recording',
    description: 'Local microphone input with intelligent silence detection. No cloud recording required.',
  },
  {
    icon: Brain,
    title: 'AI Transcription',
    description: 'Powered by OpenAI Whisper. Run locally or use the API - your choice.',
  },
  {
    icon: Code2,
    title: 'Smart Insertion',
    description: 'Language-aware parsing with proper indentation. Comments that fit your code style.',
  },
  {
    icon: Puzzle,
    title: 'Pluggable Backends',
    description: 'Swap recorders, transcribers, and parsers. Build your own integrations.',
  },
  {
    icon: Terminal,
    title: 'CLI & Python API',
    description: 'Use from terminal or import in your scripts. Jupyter notebook support included.',
  },
  {
    icon: Zap,
    title: 'Security Hardened',
    description: 'Atomic file writes, path traversal protection, preview mode, and comprehensive error handling.',
  },
];

export default function Features() {
  return (
    <section id="features" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Everything You Need for
            <span className="gradient-text"> Voice-to-Code</span>
          </h2>
          <p className="text-gray-500 text-lg max-w-2xl mx-auto">
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
              <div className="inline-flex p-3 rounded-lg bg-gray-900 mb-4 group-hover:scale-110 transition-transform">
                <feature.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-gray-500">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
