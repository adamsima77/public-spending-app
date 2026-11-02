<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class () extends Migration {
    public function up(): void
    {
        Schema::create('settled_contracts', function (Blueprint $table): void {
            $table->id();
            $table->string('notice_id', 250);
            $table->foreignId('notice_record_id')->constrained('notices')->restrictOnDelete();
            $table->string('contract_ref', 64);
            $table->text('contract_number')->nullable();
            $table->timestamp('conclusion_date')->nullable();
            $table->text('title')->nullable();
            $table->text('contract_url')->nullable();

            $table->jsonb('extra_fields')->nullable();
            $table->timestamps();

            $table->unique(['notice_record_id', 'contract_ref'], 'settled_contracts_notice_record_ref_unique');
            $table->index('notice_id');
            $table->index('conclusion_date');
        });

        Schema::table('settled_contracts', function (Blueprint $table): void {
            $table->jsonb('tender_refs')->default('[]');
        });

        Schema::create('settled_contract_tenders', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('settled_contract_id')->constrained('settled_contracts')->cascadeOnDelete();
            $table->foreignId('lot_tender_id')->constrained('lot_tenders')->restrictOnDelete();
            $table->timestamps();

            $table->unique(['settled_contract_id', 'lot_tender_id']);
            $table->index('lot_tender_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('settled_contract_tenders');
        Schema::dropIfExists('settled_contracts');
    }
};
