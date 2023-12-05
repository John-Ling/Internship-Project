import { useState } from 'react';
import { SearchBar } from './components/SearchBar';
import { ChatMessage } from './components/ChatMessage';
import { message } from "./types";
import "./assets/css/index.css";
import "./assets/css/fonts.css";

function App() {
	const [messages, setMessages] = useState<message[]>([]);

	const add_message = (message: message) => {
		const call_api = async (query: string): Promise<string> => {
			const response = await fetch("http://127.0.0.1:8080/search", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({"query": query})
			}).then(response => response.json());
			
			console.log(response);
			let context: string = response["context"];
			console.log(context);
			
			const llmResponse = await fetch("http://127.0.0.1:8080/query", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({"query": query, "context": context})
			}).then(response => response.json());

			console.log("Response");
			console.log(llmResponse);
			return llmResponse;
		}

		setMessages([...messages, message]);

		let llmResponse: Promise<string> = call_api(message.content);
		llmResponse.then((response: any) => {
			let content: string = response.choices[0].message.content;
			setMessages(old => [...old, {content: content, fromBot: true}]);
		});

		return;
	}

	let chatMessages = messages.map(message => <ChatMessage message={message}></ChatMessage>)
	return (
		<>
			<div id="main-view">
				<div id="chat-view">
					{chatMessages}
				</div>
				<SearchBar addMessage={add_message}></SearchBar>
			</div>
		</>
	)
}

export default App
