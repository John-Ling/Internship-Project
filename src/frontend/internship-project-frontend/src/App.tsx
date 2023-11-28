import { useState } from 'react';
import { SearchBar } from './components/SearchBar';
import { GreetingPage } from './components/GreetingPage';
import { ChatMessage } from './components/ChatMessage';
import { message } from "./types";
import "./assets/css/index.css";
import "./assets/css/fonts.css";

function App() {
	const [messages, setMessages] = useState<message[]>([]);

	const add_message = (message: message) => {
		const call_api = async (query: string): Promise<string> => {
			console.log("Calling API");
			// search vector database for similar text to use as context
			const response = await fetch("http://127.0.0.1:8080/search", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({"query": query})
			}).then(response => response.json());
			let context: string = response["documents"][0][0];
			console.log(context);
			
			const llmResponse = await fetch("http://127.0.0.1:8080/query", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({"query": query, "context": context})
			}).then(response => response.json());
			console.log("Response")
			console.log(llmResponse);
			return llmResponse;
		}

		setMessages([...messages, message]);

		let llmResponse: Promise<string> = call_api(message.content);
		llmResponse.then((response: any) => {
			let content: string = response.choices[0].message.content;
			console.log("Response from API");
			console.log(content);
			let message: message = {content: content, fromBot: true};
			setMessages(old => [...old, message]);
		});

		return;
	}

	let chatMessages = messages.map(message => <ChatMessage message={message}></ChatMessage>)

	return (
		<>
			<div id="main-view">
				<GreetingPage visibility={false}></GreetingPage>
				<div id="chat-view">
					{chatMessages}
				</div>
				<SearchBar addMessage={add_message}></SearchBar>
			</div>
		</>
	)
}

export default App
