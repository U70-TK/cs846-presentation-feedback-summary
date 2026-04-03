import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';

export type ProjectRecord = {
  id: string;
  name: string;
  environment: string;
  status: 'active' | 'paused';
  updatedAt: string;
};

@Injectable()
export class ProjectsService {
  constructor(private readonly db: DatabaseService) {}

  list() {
    return this.db.all<ProjectRecord>(
      'SELECT id, name, environment, status, updated_at as updatedAt FROM projects ORDER BY updated_at DESC;'
    );
  }

  create(name: string, environment: string) {
    const record: ProjectRecord = {
      id: `proj_${Math.random().toString(36).slice(2, 8)}`,
      name,
      environment,
      status: 'active',
      updatedAt: new Date().toISOString(),
    };
    this.db.run(
      'INSERT INTO projects (id, organization_id, name, environment, status, updated_at) VALUES (?, ?, ?, ?, ?, ?);',
      [record.id, 'org_001', record.name, record.environment, record.status, record.updatedAt]
    );
    return record;
  }
}
