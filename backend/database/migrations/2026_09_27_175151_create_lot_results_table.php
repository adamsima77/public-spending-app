<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('lot_results', function (Blueprint $table) {
            $table->id();
            $table->string('notice_id', 250);
            $table->string('lot_reference', 64);
            $table->foreignId('lot_id')->nullable()->constrained('notice_lots')->nullOnDelete();

            $table->string('award_outcome', 32)->nullable();
            $table->string('non_award_reason', 32)->nullable();
            $table->decimal('lowest_offer_value', 14, 2)->nullable();
            $table->string('lowest_offer_currency', 10)->nullable();
            $table->decimal('highest_offer_value', 14, 2)->nullable();
            $table->string('highest_offer_currency', 10)->nullable();

            $table->jsonb('extra_fields')->nullable();
            $table->timestamps();

            $table->unique(['notice_id', 'lot_reference']);
            $table->index('lot_id');
            $table->index('award_outcome');
        });

        DB::statement("ALTER TABLE lot_results ADD COLUMN tender_refs text[] NOT NULL DEFAULT '{}';");
        DB::statement("ALTER TABLE lot_results ADD COLUMN contract_refs text[] NOT NULL DEFAULT '{}';");

        Schema::create('lot_result_submission_stats', function (Blueprint $table) {
            $table->id();
            $table->foreignId('lot_result_id')->constrained('lot_results')->cascadeOnDelete();
            $table->string('category_code', 32);
            $table->unsignedInteger('count')->nullable();
            $table->timestamps();

            $table->unique(['lot_result_id', 'category_code']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('lot_result_submission_stats');
        Schema::dropIfExists('lot_results');
    }
};