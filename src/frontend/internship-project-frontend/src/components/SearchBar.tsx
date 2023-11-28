import { useState } from "react";
import { message } from "../types";
import "../assets/css/search_bar.css";


interface SearchBarProps  {
	addMessage: (message: message) => void;
}

export const SearchBar:React.FC<SearchBarProps> = ({addMessage}) => {
	const [query, setQuery] = useState("");
	const handle_submit = (e: any) => {
		e.preventDefault();
		let message: message = {content: query, fromBot: false}
		addMessage(message);
		setQuery("");
		return;
	}

	return (
		<>
			<form id="search-bar" onSubmit={handle_submit}>
				<input 
					type="text" 
					placeholder="Ask your question"
					value={query}
					onChange={e => setQuery(e.target.value)}
				/>
				<input
					type="submit"
				/>
			</form>
		</>
	)
}