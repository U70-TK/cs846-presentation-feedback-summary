import { Injectable } from '@nestjs/common';
import { DatabaseService } from '../../database/database.service';

@Injectable()
export class BillingService {
  constructor(private readonly db: DatabaseService) {}

  plans() {
    return [
      {
        id: 'plan_startup',
        name: 'Startup',
        price: 49,
        interval: 'month',
        seats: 5,
      },
      {
        id: 'plan_growth',
        name: 'Growth',
        price: 149,
        interval: 'month',
        seats: 25,
      },
      {
        id: 'plan_enterprise',
        name: 'Enterprise',
        price: 399,
        interval: 'month',
        seats: 100,
      },
    ];
  }

  invoices() {
    return this.db.all(
      'SELECT id, amount, status, issued_at as issuedAt FROM invoices ORDER BY issued_at DESC;'
    );
  }
}
