import Content from "./components/Content";
import Navbar from "./components/Navbar";

function App() {
  return (
    <>
      <div className="bg-slate-500">
        <Navbar />

        <div className="flex justify-center items-center flex-col h-screen  ">
          <Content />
          <button className="px-4 my-8  border-2 border-black hover:border-blue-400 rounded-lg py-4 text-cyan-300 bg-black ">
            Recognize
          </button>
        </div>
      </div>
    </>
  );
}

export default App;
