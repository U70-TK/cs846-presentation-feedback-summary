import { Injectable, OnModuleDestroy } from '@nestjs/common';
import Database from 'better-sqlite3';
import path from 'path';

@Injectable()
export class DatabaseService implements OnModuleDestroy {
  private readonly db: Database.Database;

  constructor() {
    const dbPath =
      process.env.DB_PATH ??
      path.resolve(process.cwd(), '..', 'problem_d_database', 'northwind_signal.sqlite');

    this.db = new Database(dbPath, { fileMustExist: false });
  }

  all<T = unknown>(sql: string, params?: unknown[]) {
    return params ? this.db.prepare(sql).all(params) : this.db.prepare(sql).all();
  }

  get<T = unknown>(sql: string, params?: unknown[]) {
    return params ? this.db.prepare(sql).get(params) : this.db.prepare(sql).get();
  }

  run(sql: string, params?: unknown[]) {
    return params ? this.db.prepare(sql).run(params) : this.db.prepare(sql).run();
  }

  onModuleDestroy() {
    this.db.close();
  }
}
