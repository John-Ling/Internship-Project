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
// 			query =`
// 			Context: Title: MR D.I.Y. GROUP
// ID: 5296
// Category: Consumer Cyclicals (Specialty Retailers)
// KEY STATS 
// Per Share 
// Revenue/Shr (dil.) 0.421 
// EPS Excl Extra (dil.) 0.050 
// EPS Incl Extra (dil.) 0.050 
// EPS Normalized (dil.) 0.056 
// Div/Shr Comm Stk Primary 0.02 
// Tot Cash &amp; ST Invest/Shr 0.015 
// Cash Flow/Shr (dil.) 0.078 
// Bk Val/Shr, Tot Eqty 0.152 
// Tang Bk Value, Tot Eqty 0.151 
// Dividend 
// Dividend Yield 1.76 
// Annual Dividend - 5 Yr. Avg 0.000 
// Dividend 5 Yr. Growth Rate 0.000 
// Dividend Payout Ratio 
// LFY 43.185 
// LTM 49.096 
// LFI 60.913 
// Last Dividend 
// Decl 0.008 
// Pay Date 22 Dec 2023 
// Ex-Date 04 Dec 2023 
// Profitability Ratios (%) 
// Gross Profit % Margin 41.000 
// EBITDA % Margin 26.290 
// Oper Income % Margin 17.579 
// Income Bef Tax % Margin 16.091 
// Income Aft Tax % Margin 11.866 
// Growth Rates (%) 
// Revenue, %Yr/Yr 18.15% 
// Revenue 
// 5 Yr. Growth Rate 26.526 
// 10 Yr. Growth Rate 0.00 
// EPS, %Yr/Yr (9.481%) 
// EPS 
// 5 Yr. Growth Rate 16.80 
// 10 Yr. Growth Rate 0.000 
// Dividend 
// %Yr/Yr, LFY (10.168%) 
// 5 Yr. Growth Rate 0.000 
// 10 Yr. Growth Rate 0.000 
// Valuation Ratios (MYR) 
// Curr Price/Rev/Shr 3.766 
// Curr P/E Excl Extra, LTM 27.944 
// P/E Excl Extra Items 31.800 
// Curr P/E Normalized, LFY 28.232 
// Curr Price/CF/Shr 20.310 
// Curr Price/Tang Bk, Tot Eqty 10.528 
// Curr EV/Tot Revenue (LFY) 3.820 
// Curr Mkt Cap (m) 15,011.860 
// (+) Tot Debt Cap, LFY (m) 1,637.709 
// (-) Cash &amp; Equiv, LFY (m) 137.843 
// (=) Curr EV, LFY (m) 16,511.720 

// Using the following context answer the following:
// Is Mr Diy a good long term investment?
// 			`
			console.log("Calling API");
			const response = await fetch("https://api.openai.com/v1/chat/completions", {
				method: "POST",
				headers: {"Content-Type": "application/json", "Authorization": "Bearer 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"},
				body: JSON.stringify({"model": "gpt-3.5-turbo", "messages": [{"role": "system", "content": "You are a helpful assistant"}, {"role": "user", "content": query}]})
				// body: JSON.stringify({"prompt": `${query} please keep your answer concise and under 1024 tokens:`, n_predict: 1024})
			})
			return await response.json();
		}

		setMessages([...messages, message]);

		let llmResponse: Promise<string> = call_api(message.content);
		llmResponse.then((response: any) => {
			console.log(response.choices[0].message.content)
			let botMessage: message = {content: response.choices[0].message.content, fromBot: true}
			setMessages(oldMessages => [...oldMessages, botMessage]);
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
