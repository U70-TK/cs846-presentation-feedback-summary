import { Module } from '@nestjs/common';
import { DatabaseModule } from './database/database.module';
import { HealthController } from './health.controller';
import { AuthModule } from './modules/auth/auth.module';
import { BillingModule } from './modules/billing/billing.module';
import { OrganizationsModule } from './modules/organizations/organizations.module';
import { ProjectsModule } from './modules/projects/projects.module';
import { UsageModule } from './modules/usage/usage.module';

@Module({
  imports: [DatabaseModule, AuthModule, BillingModule, OrganizationsModule, ProjectsModule, UsageModule],
  controllers: [HealthController],
})
export class AppModule {}
