import { useState } from 'react';
import { Copy, Check, Terminal, Package, Download } from 'lucide-react';

type TabType = 'pip' | 'source' | 'prereq';

export default function Installation() {
  const [activeTab, setActiveTab] = useState<TabType>('pip');
  const [copied, setCopied] = useState<string | null>(null);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(null), 2000);
  };

  const tabs: { id: TabType; label: string; icon: typeof Terminal }[] = [
    { id: 'pip', label: 'pip install', icon: Package },
    { id: 'source', label: 'From Source', icon: Download },
    { id: 'prereq', label: 'Prerequisites', icon: Terminal },
  ];

  const commands = {
    pip: 'pip install speakline',
    source: `git clone https://github.com/likthvishal/SpeakLine
cd SpeakLine
pip install -e .`,
    prereq: {
      macos: 'brew install portaudio',
      ubuntu: 'sudo apt-get install portaudio19-dev',
      windows: '# PortAudio usually bundled on Windows',
    },
  };

  return (
    <section id="installation" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Get Started in
            <span className="gradient-text"> Seconds</span>
          </h2>
          <p className="text-gray-500 text-lg max-w-2xl mx-auto">
            Install SpeakLine and start recording your first comment in under a minute.
          </p>
        </div>

        {/* Installation Card */}
        <div className="max-w-3xl mx-auto">
          <div className="glass rounded-2xl overflow-hidden">
            {/* Tabs */}
            <div className="flex border-b border-gray-200">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 px-4 py-3 flex items-center justify-center gap-2 text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'text-gray-900 bg-gray-50 border-b-2 border-gray-900'
                      : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Content */}
            <div className="p-6">
              {activeTab === 'pip' && (
                <div>
                  <p className="text-gray-500 mb-4">Install directly from PyPI:</p>
                  <div className="code-block relative group">
                    <pre className="p-4">
                      <code className="text-green-700">{commands.pip}</code>
                    </pre>
                    <button
                      onClick={() => copyToClipboard(commands.pip, 'pip')}
                      className="absolute top-3 right-3 p-2 rounded-lg bg-gray-100 text-gray-400 hover:text-gray-900 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      {copied === 'pip' ? <Check className="w-4 h-4 text-green-700" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              )}

              {activeTab === 'source' && (
                <div>
                  <p className="text-gray-500 mb-4">Clone and install for development:</p>
                  <div className="code-block relative group">
                    <pre className="p-4">
                      <code className="text-gray-700">
                        {commands.source.split('\n').map((line, i) => (
                          <div key={i}>
                            <span className="text-green-700">$</span> {line}
                          </div>
                        ))}
                      </code>
                    </pre>
                    <button
                      onClick={() => copyToClipboard(commands.source, 'source')}
                      className="absolute top-3 right-3 p-2 rounded-lg bg-gray-100 text-gray-400 hover:text-gray-900 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      {copied === 'source' ? <Check className="w-4 h-4 text-green-700" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
              )}

              {activeTab === 'prereq' && (
                <div className="space-y-4">
                  <p className="text-gray-500">Install PortAudio for your platform:</p>

                  {Object.entries(commands.prereq).map(([platform, cmd]) => (
                    <div key={platform}>
                      <p className="text-sm text-gray-400 mb-2 capitalize">{platform}</p>
                      <div className="code-block relative group">
                        <pre className="p-3">
                          <code className="text-gray-700">
                            <span className="text-green-700">$</span> {cmd}
                          </code>
                        </pre>
                        <button
                          onClick={() => copyToClipboard(cmd, platform)}
                          className="absolute top-2 right-2 p-1.5 rounded-lg bg-gray-100 text-gray-400 hover:text-gray-900 opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          {copied === platform ? <Check className="w-3 h-3 text-green-700" /> : <Copy className="w-3 h-3" />}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Quick Start */}
              <div className="mt-8 pt-6 border-t border-gray-200">
                <h4 className="text-gray-900 font-medium mb-3">Quick Start</h4>
                <div className="code-block">
                  <pre className="p-4 text-sm">
                    <code>
                      <div className="text-gray-400"># Record and insert comment at line 42</div>
                      <div>
                        <span className="text-green-700">$</span>{' '}
                        <span className="text-blue-600">speakline</span>{' '}
                        <span className="text-orange-600">record</span>{' '}
                        <span className="text-gray-700">myfile.py 42</span>
                      </div>
                      <div className="mt-2 text-gray-400"># Or just transcribe</div>
                      <div>
                        <span className="text-green-700">$</span>{' '}
                        <span className="text-blue-600">speakline</span>{' '}
                        <span className="text-orange-600">transcribe</span>
                      </div>
                    </code>
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
