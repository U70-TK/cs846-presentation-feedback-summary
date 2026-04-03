import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';

@Injectable()
export class OrganizationsService {
  constructor(private readonly db: DatabaseService) {}

  list() {
    return this.db.all('SELECT id, name, region, seats FROM organizations ORDER BY name ASC;');
  }
}
