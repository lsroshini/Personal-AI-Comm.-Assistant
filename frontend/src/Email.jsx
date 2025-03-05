import React, { useState } from "react";
import axios from "axios";

function Email() {
  const [emails, setEmails] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [summaries, setSummaries] = useState([]);
  const [emailText, setEmailText] = useState("");
  const [smartReplies, setSmartReplies] = useState([]);

  const fetchEmails = async () => {
    const response = await axios.get("http://localhost:5000/fetch-emails");
    setEmails(response.data.emails);
  };

  const processEmails = async () => {
    const response = await axios.post("http://localhost:5000/process-emails");
    setTasks(response.data.tasks);
    setSummaries(response.data.summaries);
  };

  const getSmartReply = async () => {
    const response = await axios.post("http://localhost:5000/smart-reply", { email_text: emailText });
    setSmartReplies(response.data.smart_replies);
  };

  return (
    <div className="p-5">
      <h1 className="text-xl font-bold">Email Processor</h1>
      <button onClick={fetchEmails} className="bg-blue-500 text-white p-2 m-2">Fetch Emails</button>
      <button onClick={processEmails} className="bg-green-500 text-white p-2 m-2">Process Emails</button>

      <h2 className="text-lg mt-4">Emails</h2>
      <ul>
        {emails.map((email, index) => (
          <li key={email.id || index} className="border p-3 rounded-md mb-2 shadow">
            <strong>From:</strong> {email.sender} <br />
            <strong>Content:</strong>
            <div
              className="border p-2 rounded bg-gray-100 mt-2"
              dangerouslySetInnerHTML={{ __html: email.content }}
            />
          </li>
        ))}
      </ul>

      <h2 className="text-lg mt-4">Tasks</h2>
      <ul>
        {tasks.map((task, index) => (
          <li key={index} className="border p-2 rounded-md bg-yellow-100 mb-1">
            {task.description} - <strong>Priority:</strong> {task.priority_score}
          </li>
        ))}
      </ul>

      <h2 className="text-lg mt-4">Summaries</h2>
      <ul>
        {summaries.map((summaryObj, index) => (
          <li key={index} className="border p-2 rounded-md bg-blue-100 mb-1">
            {summaryObj.summary} {/* Ensure you're accessing the correct property */}
          </li>
        ))}
      </ul>


      <h2 className="text-lg mt-4">Smart Reply</h2>
      <input 
        type="text" 
        value={emailText} 
        onChange={(e) => setEmailText(e.target.value)} 
        className="border p-2 w-full" 
        placeholder="Enter email text"
      />
      <button onClick={getSmartReply} className="bg-purple-500 text-white p-2 m-2">Generate Smart Reply</button>

      <ul>
        {(Array.isArray(smartReplies) ? smartReplies : []).map((reply, index) => (
          <li key={index} className="border p-2 rounded-md bg-gray-100 mb-1">
            {reply}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Email;
