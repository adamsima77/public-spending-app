<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class () extends Migration {
    public function up(): void
    {
        Schema::table('etl_logs', function (Blueprint $table): void {
            $table->index(['created_at', 'id'], 'etl_logs_created_id_index');
            $table->index(['file_id', 'created_at', 'id'], 'etl_logs_file_created_id_index');
            $table->index(['level', 'created_at', 'id'], 'etl_logs_level_created_id_index');
        });

        Schema::table('downloaded_files', function (Blueprint $table): void {
            $table->index(['created_at', 'id'], 'downloaded_files_created_id_index');
            $table->index(['status_id', 'created_at', 'id'], 'downloaded_files_status_created_id_index');
            $table->index(['format', 'created_at', 'id'], 'downloaded_files_format_created_id_index');
        });

        Schema::table('system_logs', function (Blueprint $table): void {
            $table->index(['created_at', 'id'], 'system_logs_created_id_index');
            $table->index(['user_id', 'created_at', 'id'], 'system_logs_user_created_id_index');
            $table->index(['type', 'created_at', 'id'], 'system_logs_type_created_id_index');
            $table->index(['event', 'created_at', 'id'], 'system_logs_event_created_id_index');
        });

        Schema::table('notices', function (Blueprint $table): void {
            $table->index(['created_at', 'id'], 'notices_created_id_index');
            $table->index(['procedure_id', 'created_at', 'id'], 'notices_procedure_created_id_index');
            $table->index(['is_latest', 'created_at', 'id'], 'notices_latest_created_id_index');
        });

        Schema::table('notice_lots', function (Blueprint $table): void {
            $table->index(['created_at', 'id'], 'notice_lots_created_id_index');
            $table->index(['procedure_id', 'created_at', 'id'], 'notice_lots_procedure_created_id_index');
            $table->index(['main_cpv', 'created_at', 'id'], 'notice_lots_cpv_created_id_index');
            $table->index(['nuts_code', 'created_at', 'id'], 'notice_lots_nuts_created_id_index');
            $table->index(['eu_funded', 'created_at', 'id'], 'notice_lots_eu_created_id_index');
        });

        Schema::table('procedures', function (Blueprint $table): void {
            $table->index(['created_at', 'id'], 'procedures_created_id_index');
            $table->index(['buyer_id', 'created_at', 'id'], 'procedures_buyer_created_id_index');
            $table->index(['main_cpv', 'created_at', 'id'], 'procedures_cpv_created_id_index');
            $table->index(['nuts_code', 'created_at', 'id'], 'procedures_nuts_created_id_index');
            $table->index(['procedure_type', 'created_at', 'id'], 'procedures_type_created_id_index');
        });

        Schema::table('organizations', function (Blueprint $table): void {
            $table->index(['country', 'id'], 'organizations_country_id_index');
            $table->index(['nuts_code', 'id'], 'organizations_nuts_id_index');
            $table->index(['company_size', 'id'], 'organizations_size_id_index');
        });
    }

    public function down(): void
    {
        Schema::table('organizations', function (Blueprint $table): void {
            $table->dropIndex('organizations_country_id_index');
            $table->dropIndex('organizations_nuts_id_index');
            $table->dropIndex('organizations_size_id_index');
        });

        Schema::table('procedures', function (Blueprint $table): void {
            $table->dropIndex('procedures_created_id_index');
            $table->dropIndex('procedures_buyer_created_id_index');
            $table->dropIndex('procedures_cpv_created_id_index');
            $table->dropIndex('procedures_nuts_created_id_index');
            $table->dropIndex('procedures_type_created_id_index');
        });

        Schema::table('notice_lots', function (Blueprint $table): void {
            $table->dropIndex('notice_lots_created_id_index');
            $table->dropIndex('notice_lots_procedure_created_id_index');
            $table->dropIndex('notice_lots_cpv_created_id_index');
            $table->dropIndex('notice_lots_nuts_created_id_index');
            $table->dropIndex('notice_lots_eu_created_id_index');
        });

        Schema::table('notices', function (Blueprint $table): void {
            $table->dropIndex('notices_created_id_index');
            $table->dropIndex('notices_procedure_created_id_index');
            $table->dropIndex('notices_latest_created_id_index');
        });

        Schema::table('system_logs', function (Blueprint $table): void {
            $table->dropIndex('system_logs_created_id_index');
            $table->dropIndex('system_logs_user_created_id_index');
            $table->dropIndex('system_logs_type_created_id_index');
            $table->dropIndex('system_logs_event_created_id_index');
        });

        Schema::table('downloaded_files', function (Blueprint $table): void {
            $table->dropIndex('downloaded_files_created_id_index');
            $table->dropIndex('downloaded_files_status_created_id_index');
            $table->dropIndex('downloaded_files_format_created_id_index');
        });

        Schema::table('etl_logs', function (Blueprint $table): void {
            $table->dropIndex('etl_logs_created_id_index');
            $table->dropIndex('etl_logs_file_created_id_index');
            $table->dropIndex('etl_logs_level_created_id_index');
        });
    }
};
