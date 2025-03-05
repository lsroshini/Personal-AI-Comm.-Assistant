import React, { useState } from "react";
import axios from "axios";

const Slack = () => {
  const [channelId, setChannelId] = useState("");
  const [digest, setDigest] = useState("");
  const [loading, setLoading] = useState(false);

  const generateDigest = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:5000/daily_digest?channel_id=${channelId}`);
      setDigest(response.data.digest || "No digest available.");
    } catch (error) {
      console.error("Error generating digest", error);
      setDigest("Error fetching digest.");
    }
    setLoading(false);
  };
  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Slack Task Manager</h1>

      {/* Input for Channel ID */}
      <input
        type="text"
        placeholder="Enter Channel ID"
        value={channelId}
        onChange={(e) => setChannelId(e.target.value)}
        className="border p-2 w-full mb-2"
      />

      {/* Buttons */}
      <div className="flex gap-2 mb-4">
        <button onClick={generateDigest} className="bg-purple-500 text-white px-4 py-2 rounded">
          Generate Daily Digest
        </button>
      </div>

      {loading && <p className="text-blue-600">Loading...</p>}

      <h2 className="text-xl font-semibold mt-6">Daily Digest</h2>
      <pre className="border p-4 rounded bg-gray-100 overflow-x-auto">
        {digest || "No digest available."}
      </pre>
    </div>
  );
};

export default Slack;
