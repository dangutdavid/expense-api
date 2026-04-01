from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5ceab8319b54"
down_revision: Union[str, Sequence[str], None] = "f6eda6e93990"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "expenses",
        sa.Column("status", sa.String(), nullable=False, server_default="draft"),
    )

    op.execute("UPDATE expenses SET status = 'draft' WHERE status IS NULL")

    op.alter_column("expenses", "status", server_default=None)


def downgrade() -> None:
    op.drop_column("expenses", "status")