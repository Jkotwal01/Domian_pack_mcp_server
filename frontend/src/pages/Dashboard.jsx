/**
 * Dashboard Page
 */
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, FileText, History, Plus } from 'lucide-react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import useChatStore from '../stores/chatStore';

const Dashboard = () => {
  const navigate = useNavigate();
  const { sessions, loadSessions, createSession } = useChatStore();

  useEffect(() => {
    loadSessions();
  }, []);

  const handleNewSession = async () => {
    const session = await createSession('default-domain-pack');
    if (session) {
      navigate('/chat');
    }
  };

  const stats = [
    {
      label: 'Active Sessions',
      value: sessions.length,
      icon: MessageSquare,
      color: 'primary',
    },
    {
      label: 'Pending Proposals',
      value: 0,
      icon: FileText,
      color: 'secondary',
    },
    {
      label: 'Total Versions',
      value: 0,
      icon: History,
      color: 'success',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Welcome to your Domain Pack Authoring workspace
          </p>
        </div>
        <Button
          variant="primary"
          icon={Plus}
          onClick={handleNewSession}
        >
          New Session
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <Card key={stat.label} hover className="cursor-pointer">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg bg-${stat.color}-100`}>
                <stat.icon className={`w-6 h-6 text-${stat.color}-600`} />
              </div>
              <div>
                <p className="text-sm text-gray-600">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Recent Sessions */}
      <Card title="Recent Sessions">
        {sessions.length === 0 ? (
          <div className="text-center py-12">
            <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No sessions yet</p>
            <p className="text-sm text-gray-500 mt-1">
              Create a new session to get started
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {sessions.slice(0, 5).map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => navigate('/chat')}
              >
                <div>
                  <p className="font-medium text-gray-900">
                    Session {session.id.slice(0, 8)}
                  </p>
                  <p className="text-sm text-gray-500">
                    {new Date(session.created_at).toLocaleString()}
                  </p>
                </div>
                <Badge variant={session.is_active ? 'success' : 'gray'}>
                  {session.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

export default Dashboard;
