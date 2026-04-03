import { Controller, Get } from '@nestjs/common';
import { BillingService } from './billing.service';

@Controller('billing')
export class BillingController {
  constructor(private readonly billingService: BillingService) {}

  @Get('plans')
  plans() {
    return this.billingService.plans();
  }

  @Get('invoices')
  invoices() {
    return this.billingService.invoices();
  }
}
