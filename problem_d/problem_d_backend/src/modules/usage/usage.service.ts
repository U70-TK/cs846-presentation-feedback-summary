import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';

@Injectable()
export class UsageService {
  constructor(private readonly db: DatabaseService) {}

  summary() {
    return this.db.get(
      'SELECT ingestion_gb as ingestionGb, model_calls as modelCalls, team_seats as teamSeats, last_sync as lastSync FROM usage_summary LIMIT 1;'
    );
  }
}
