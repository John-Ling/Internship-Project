import { message } from "../types";
import "../assets/css/chat_message.css";


interface ChatMessageProps {
	message: message;
}

export const ChatMessage:React.FC<ChatMessageProps> = ({message}) => {
	return (
		<>
			<div className={message.fromBot ? "bot-message message" : "user-message message"}>
				<p>{message.content}</p>
			</div>
		</>
	);
}