import { SearchBar } from './components/SearchBar';
import { GreetingPage } from './components/GreetingPage';
import { ChatMessage } from './components/ChatMessage';
import "./assets/css/index.css";
import "./assets/css/fonts.css";

function App() {
  return (
    <>
      <div id="main-view">
        <GreetingPage visibility={false}></GreetingPage>
        <ChatMessage messageContent='Hello' fromBot={true}></ChatMessage>
        <ChatMessage messageContent='Hello'></ChatMessage>
        <SearchBar></SearchBar>
      </div>
    </>
  )
}

export default App
