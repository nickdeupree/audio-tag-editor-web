import Image from "next/image";
import Header from "./components/Header";
import Workspace from "./components/Workspace";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header/>
      <main className="flex-1 flex justify-center items-start pt-12 px-4 md:px-8 pb-8">
        <Workspace />
      </main>
    </div>
  );
}
