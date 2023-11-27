import { useState } from "react";
import "../assets/css/search_bar.css";

export const SearchBar = () => {
	const handle_submit = (e: any) => {
		e.preventDefault();
		return;
	}

	return (
		<>
			<form id="search-bar" onSubmit={handle_submit}>
				<input 
					type="text" 
					placeholder="Ask your question"
				/>
				<input
					type="submit"
				/>
			</form>
		</>
	)
}