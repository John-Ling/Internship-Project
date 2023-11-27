import { useState } from "react";
import "../assets/css/greeting_page.css";

export const GreetingPage:React.FC<{visibility: boolean}> = ({visibility}) => {
	const [visible, setVisible] = useState<boolean>(visibility);
	return (
		visible ?
		<>
			<div id="greeting-page">
				<h2>Ask Mr Guru</h2>
			</div>
		</>
		: 
		<></>
	)
}