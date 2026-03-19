import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Features from './components/Features';
import Demo from './components/Demo';
import Installation from './components/Installation';
import Languages from './components/Languages';
import ApiSection from './components/ApiSection';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <main>
        <Hero />
        <Features />
        <Demo />
        <Installation />
        <Languages />
        <ApiSection />
      </main>
      <Footer />
    </div>
  );
}

export default App;
