import { useState } from 'react';
import { Menu, X, Mic, Github } from 'lucide-react';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  const navLinks = [
    { href: '#features', label: 'Features' },
    { href: '#demo', label: 'Demo' },
    { href: '#installation', label: 'Installation' },
    { href: '#languages', label: 'Languages' },
    { href: '#api', label: 'API' },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <a href="#" className="flex items-center gap-2 group">
            <div className="p-2 rounded-lg bg-gradient-to-br from-sky-500 to-violet-500 group-hover:scale-110 transition-transform">
              <Mic className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">SpeakLine</span>
          </a>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="text-slate-400 hover:text-white transition-colors text-sm font-medium"
              >
                {link.label}
              </a>
            ))}
          </div>

          {/* CTA Buttons */}
          <div className="hidden md:flex items-center gap-3">
            <a
              href="https://github.com/likthvishal/SpeakLine"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary flex items-center gap-2 text-sm py-2"
            >
              <Github className="w-4 h-4" />
              GitHub
            </a>
            <a href="#installation" className="btn-primary text-sm py-2">
              Get Started
            </a>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-slate-400 hover:text-white"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden py-4 border-t border-slate-800">
            {navLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                className="block py-2 text-slate-400 hover:text-white transition-colors"
                onClick={() => setIsOpen(false)}
              >
                {link.label}
              </a>
            ))}
            <div className="flex gap-3 mt-4">
              <a href="https://github.com" className="btn-secondary text-sm py-2 flex-1 text-center">
                GitHub
              </a>
              <a href="#installation" className="btn-primary text-sm py-2 flex-1 text-center">
                Get Started
              </a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
